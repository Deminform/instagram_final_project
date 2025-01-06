from fastapi import (
    Query,
    status,
    UploadFile,
    File,
    Form,
    Path,
)

from fastapi import Depends, APIRouter
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from conf import messages, const
from database.db import get_db
from src.posts.models import Post
from src.posts.post_service import PostService
from src.posts.schemas import PostResponseSchema, PostUpdateRequest
from src.services.auth.auth_service import get_current_user
from src.users.models import User

router = APIRouter(prefix="/posts", tags=["posts"])
router_admin = APIRouter(prefix="/admin/posts", tags=["posts"])


@router.get("/", response_model=list[PostResponseSchema])
async def get_posts(
        limit: int = Query(10, ge=10, le=100),
        offset: int = Query(0, ge=0),
        tag: str = Query(None, description="Search by tags, partial match, case insensitive"),
        keyword: str = Query(None, description="Search by description, partial match, case insensitive"),
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
) -> list[PostResponseSchema]:
    """
    Retrieve a list of posts with optional filters and pagination.

    :param limit: Maximum number of posts to retrieve, default is 10.
    :param offset: Number of posts to skip, default is 0.
    :param tag: Filter posts by tags (partial match, case-insensitive).
    :param keyword: Filter posts by description (partial match, case-insensitive).
    :param db: Database session dependency.
    :param user: Current authenticated user dependency.
    :return: List of posts matching the criteria.
    """
    post_service = PostService(db)
    return await post_service.get_posts(limit, offset, keyword, tag)


@router.get("/{post_id}", response_model=PostResponseSchema)
async def get_post_by_id(
        post_id: int = Path(..., ge=1, le=2147483647),
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
) -> Post:
    """
    Retrieve a specific post by its ID.

    :param post_id: The unique identifier of the post.
    :param db: Database session dependency.
    :param user: Current authenticated user dependency.
    :return: The post matching the provided ID.
    """
    post_service = PostService(db)
    return await post_service.get_post_by_id(post_id)


@router.post("/", response_model=PostResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_post(
        description: str = Form(...,
            min_length=const.POST_DESCRIPTION_MIN_LENGTH,
            max_length=const.POST_DESCRIPTION_MAX_LENGTH,
            description=messages.POST_DESCRIPTION
),
        tags: str = Form(None, description=messages.TAG_DESCRIPTION),
        image: UploadFile = File(...),
        image_filter: str | None = Form(None, description=messages.IMAGE_FILTER_DESCRIPTION, enum=[
        "grayscale",
        "thumbnail",
        "blur",
        "crop",
        "negate",
        "vignette",
        "brightness",
        "contrast",
        "saturation",
        "hue",
        "invert",
        "sharpen",
        "noise",
        "oil_painting",
        "pixelate",
        "posterize",
        ]),
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
) -> Post:
    """
    Create a new post with the provided description, image, tags, and filter.

    :param description: Description of the post, required with length constraints.
    :param image_filter: Optional image filter to apply.
    :param tags: Optional comma-separated tags for the post.
    :param image: The uploaded image file.
    :param db: Database session dependency.
    :param user: Current authenticated user dependency.
    :return: The created post.
    """
    post_service = PostService(db)
    return await post_service.create_post(user, description, image_filter, tags, image)


@router.post("/{post_id}/qr", status_code=status.HTTP_200_OK)
async def create_qr(
        post_id: int = Path(..., ge=1, le=2147483647),
        image_filter: str = Form(None, description=messages.IMAGE_FILTER_DESCRIPTION, enum=[
            "grayscale",
            "thumbnail",
            "blur",
            "crop",
            "negate",
            "vignette",
            "brightness",
            "contrast",
            "saturation",
            "hue",
            "invert",
            "sharpen",
            "noise",
            "oil_painting",
            "pixelate",
            "posterize",
        ]),
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    """
    Generate a QR code for a specific post.

    :param post_id: The unique identifier of the post.
    :param image_filter: Filter to apply to the QR code image.
    :param db: Database session dependency.
    :param user: Current authenticated user dependency.
    :return: Streaming response containing the QR code image.
    """
    post_service = PostService(db)
    return StreamingResponse(
        await post_service.create_qr(user, post_id, image_filter),
        media_type="image/png"
    )


@router.put("/{post_id}", response_model=PostResponseSchema)
async def edit_post(
        body: PostUpdateRequest,
        post_id: int = Path(..., ge=1, le=2147483647),
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
) -> Post:
    """
    Update the description of a specific post.

    :param post_id: The unique identifier of the post to update.
    :param body: Request body containing the new description.
    :param db: Database session dependency.
    :param user: Current authenticated user dependency.
    :return: The updated post.
    """
    post_service = PostService(db)
    return await post_service.update_post_description(user, post_id, body.description)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
        post_id: int = Path(..., ge=1, le=2147483647),
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    """
    Delete a specific post by its ID along with associated data.

    :param post_id: The unique identifier of the post to delete.
    :param db: Database session dependency.
    :param user: Current authenticated user dependency.
    :return: The deleted post instance.
    """
    post_service = PostService(db)
    return await post_service.delete_post(user, post_id)
