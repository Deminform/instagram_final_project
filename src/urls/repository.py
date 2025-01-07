from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from src.urls.models import URLs


class URLRepository:
    """
    A repository class for performing database operations on URLs.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize the URLRepository with a database session.

        :param db: The asynchronous database session.
        """
        self.session = db

    async def add_image(self, post_id: int, image_url: str, image_filter: str):
        """
        Add a new edited image record to the database.

        :param post_id: The ID of the post associated with the image.
        :param image_url: The URL of the edited image.
        :param image_filter: The filter applied to the image.
        :return: The created image record.
        """
        edited_image = URLs(
            post_id=post_id,
            image_url=image_url,
            image_filter=image_filter,
        )

        self.session.add(edited_image)
        await self.session.commit()
        return edited_image

    async def get_image(self, post_id: int, image_filter: str):
        """
        Retrieve an edited image by post ID and filter.

        :param post_id: The ID of the post associated with the image.
        :param image_filter: The filter applied to the image.
        :return: The image record if found, otherwise None.
        """
        stmt = select(URLs).filter_by(post_id=post_id, image_filter=image_filter)

        edited_image = await self.session.execute(stmt)
        return edited_image.scalar_one_or_none()

    async def delete_urls_by_post_id(self, post_id: int):
        """
        Delete all URLs associated with a given post ID.

        :param post_id: The ID of the post whose URLs should be deleted.
        """
        stmt = delete(URLs).filter(URLs.post_id == post_id)

        await self.session.execute(stmt)