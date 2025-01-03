from fastapi import File, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from conf import messages, const
from src.comments.repository import CommentRepository
from src.posts.models import Post
from src.scores.repository import ScoreRepository
from src.urls.image_service import URLService
from src.services.qr_service import QRService
from src.posts.repository import PostRepository
from src.tags.tag_service import TagService
from src.urls.repository import URLRepository
from src.users.models import User
from src.services.cloudinary_service import CloudinaryService
from src.users.schemas import RoleEnum


class PostService:
    def __init__(self, db: AsyncSession):
        self.image_service = URLService(db)
        self.image_repository = URLRepository(db)
        self.cloudinary_service = CloudinaryService
        self.tag_service = TagService(db)
        self.qr_service = QRService
        self.post_repository = PostRepository(db)
        self.score_repository = ScoreRepository(db)
        self.comment_repository = CommentRepository(db)

    async def _get_post_or_exception(self, post_id: int, user: User = None) -> Post:
        """
        Retrieve a post by its ID or raise an exception if not found or unauthorized.

        :param post_id: The unique identifier of the post.
        :param user: Optional User instance for permission validation.
        :return: The Post instance if found and authorized.
        """
        post = await self.post_repository.get_post_by_id(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=messages.POST_NOT_FOUND,
            )
        if user and post.user_id != user.id and user.role_name != RoleEnum.ADMIN.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=messages.FORBIDDEN,
            )
        return post


    async def create_post(self, user: User, description: str, image_filter: str, tags: str, image: File) -> Post:
        """
        Create a new post with the provided data, including image processing and tag handling.

        :param user: The User instance creating the post.
        :param description: The description of the post.
        :param image_filter: The filter to apply to the image.
        :param tags: A comma-separated string of tags.
        :param image: The uploaded image file.
        :return: The created Post instance.
        """
        await self.check_description(description)
        await self.check_image_filter(image_filter)

        image_urls = await self.cloudinary_service.get_image_urls(image, image_filter)
        tags = await self.tag_service.check_and_format_tag(tags)

        try:
            tags = await self.tag_service.get_or_create_tags(tags)
            post = await self.post_repository.create_post(user, description, tags, image_urls)

            if image_urls[const.EDITED_IMAGE_URL] != image_urls[const.ORIGINAL_IMAGE_URL]:
                await self.image_service.create_image(post.id, post.image_url, image_filter)

        except IntegrityError as e:
            await self.post_repository.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{messages.DATA_INTEGRITY_ERROR}. -//- {e}",
            )
        return post


    async def get_post_by_id(self, post_id: int) -> Post:
        """
        Retrieve a post by its unique ID.

        :param post_id: The unique identifier of the post.
        :return: The Post instance if found.
        """
        post = await self._get_post_or_exception(post_id)
        return post


    async def get_posts(self, limit: int, offset: int, keyword: str, tag: str):
        """
        Retrieve a paginated list of posts with optional filtering by keyword and tag.

        :param limit: The maximum number of posts to return.
        :param offset: The number of posts to skip.
        :param keyword: A keyword to filter posts by description.
        :param tag: A tag to filter posts by associated tags.
        :return: A list of posts matching the criteria.
        """
        return await self.post_repository.get_posts(limit, offset, keyword, tag)


    async def update_post_description(self, user, post_id: int, description: str) -> Post:
        """
        Update the description of a post owned by the user.

        :param user: The User instance requesting the update.
        :param post_id: The unique identifier of the post to update.
        :param description: The new description for the post.
        :return: The updated Post instance.
        """
        await self.check_description(description)
        post = await self._get_post_or_exception(post_id, user)
        return await self.post_repository.update_post_description(post, description)


    async def delete_post(self, user: User, post_id: int) -> Post:
        """
        Delete a post and its associated data (comments, scores, URLs).

        :param user: The User instance requesting the deletion.
        :param post_id: The unique identifier of the post to delete.
        :return: The deleted Post instance.
        """

        try:
            # delete all rating
            scores_list = await self.score_repository.delete_scores_by_post_id(post_id)

            # delete all comments
            comments_list = await self.comment_repository.delete_comment_by_post_id(post_id)

            # delete all URLs/urls
            urls_list = await self.image_repository.delete_urls_by_post_id(post_id)

            # delete post
            post = await self._get_post_or_exception(post_id, user)
            await self.post_repository.delete_post(post)

            # commit
            await self.post_repository.session.commit()
        except IntegrityError as e:
            await self.post_repository.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{messages.DATA_INTEGRITY_ERROR}. -//- {e}",
            )
        return post


    async def create_qr(self, user, post_id: int, image_filter: str):
        """
        Generate a QR code for the original image of a post with a specified filter.

        :param user: The User instance requesting the QR code.
        :param post_id: The unique identifier of the post.
        :param image_filter: The filter to apply to the QR code image.
        :return: The generated QRService instance.
        """
        await self.check_image_filter(image_filter)
        post = await self._get_post_or_exception(post_id, user)
        return await self.image_service.generate_qr(post.id, post.original_image_url, image_filter)


    @staticmethod
    async def check_description(description) -> None:
        """
        Validate the post description length against defined constraints.

        :param description: The description to validate.
        :raises HTTPException: If the description is invalid.
        """
        if const.POST_DESCRIPTION_MIN_LENGTH > len(description) or len(description) > const.POST_DESCRIPTION_MAX_LENGTH or not description:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=messages.POST_DESCRIPTION
            )


    @staticmethod
    async def check_image_filter(image_filter) -> None:
        """
        Validate the provided image filter against available options.

        :param image_filter: The image filter to validate.
        :raises HTTPException: If the filter is invalid.
        """
        if image_filter and image_filter not in const.FILTER_DICT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=messages.FILTER_IMAGE_ERROR_DETAIL
            )