from api.dependencies.database import DbSessionDep
from api.dependencies.pagination import PaginationDep
from db.crud.blog_post import BlogPostCrud
from fastapi import APIRouter, Response, status
from logging_setup import setup_gunicorn_logging
from mirror import methods as mirror_methods
from schemas import blog_post as blog_post_schemas

router = APIRouter(
    prefix="/blog",
    tags=["Blog posts"],
)

logger = setup_gunicorn_logging(__name__)


@router.post("", status_code=201, response_model=blog_post_schemas.OutBlogPostSchema)
async def create_a_blog_post(
    blog_post: blog_post_schemas.InBlogPostSchema,
    db: DbSessionDep,
):
    logger.info("inside 'create_a_blog_post'")
    crud = BlogPostCrud(db)
    result = await crud.create(blog_post)
    await crud.commit_session()
    logger.info("create_a_blog_post completed, now mirroring...")
    try:
        await mirror_methods.create_a_blog_post(blog_post)
        logger.info("mirroring create_a_blog_post completed")
    except Exception as e:
        logger.exception(
            "mirroring create_a_blog_post failed",
            exc_info=e,
            extra={
                "blog_post": blog_post,
                "result": result,
            },
        )
    return result


@router.get("", response_model=blog_post_schemas.PaginatedBlogPostSchema)
async def list_blog_posts(
    db: DbSessionDep,
    pagination: PaginationDep,
):
    logger.info("inside 'list_blog_posts'")
    logger.info("mirroring list_blog_posts...")
    try:
        await mirror_methods.list_blog_posts(
            limit=pagination.limit, offset=pagination.offset
        )
        logger.info("mirroring list_blog_posts completed")
    except Exception as e:
        logger.exception(
            "mirroring list_blog_posts failed",
            exc_info=e,
            extra={
                "limit": pagination.limit,
                "offset": pagination.offset,
            },
        )
    crud = BlogPostCrud(db)
    return await crud.get_paginated_list(pagination.limit, pagination.offset)


@router.get(
    "/{post_id}",
    response_model=blog_post_schemas.OutBlogPostSchema,
    responses={
        404: {
            "description": "Object not found",
        },
    },
)
async def retrieve_a_blog_post(
    post_id: int,
    db: DbSessionDep,
):
    logger.info("inside 'retrieve_a_blog_post'")
    logger.info("mirroring retrieve_a_blog_post...")
    try:
        await mirror_methods.retrieve_a_blog_post(post_id=post_id)
        logger.info("mirroring retrieve_a_blog_post completed")
    except Exception as e:
        logger.exception(
            "mirroring retrieve_a_blog_post failed",
            exc_info=e,
            extra={
                "post_id": post_id,
            },
        )
    crud = BlogPostCrud(db)
    return await crud.get_by_id(post_id)


@router.patch(
    "/{post_id}",
    response_model=blog_post_schemas.OutBlogPostSchema,
    responses={
        404: {
            "description": "Object not found",
        },
    },
)
async def update_a_blog_post(
    post_id: int,
    blog_post: blog_post_schemas.UpdateBlogPostSchema,
    db: DbSessionDep,
):
    logger.info("inside update_a_blog_post")
    crud = BlogPostCrud(db)
    await crud.update_by_id(post_id, blog_post)
    result = await crud.get_by_id(post_id)
    await crud.commit_session()
    logger.info("update_a_blog_post success, now mirroring...")
    try:
        await mirror_methods.update_a_blog_post(post_id=post_id, body=blog_post)
        logger.info("mirroring update_a_blog_post completed")
    except Exception as e:
        logger.exception(
            "mirroring update_a_blog_post failed",
            exc_info=e,
            extra={
                "post_id": post_id,
                "body": blog_post.model_dump(),
            },
        )
    return result


@router.delete(
    "/{post_id}",
    status_code=204,
    responses={
        404: {
            "description": "Object not found",
        },
    },
)
async def delete_a_blog_post(
    post_id: int,
    db: DbSessionDep,
):
    logger.info("inside delete_a_blog_post")
    crud = BlogPostCrud(db)
    await crud.delete_by_id(post_id)
    await crud.commit_session()
    logger.info("delete_a_blog_post success, now mirroring...")
    try:
        await mirror_methods.delete_a_blog_post(post_id=post_id)
        logger.info("mirroring delete_a_blog_post completed")
    except Exception as e:
        logger.exception(
            "mirroring delete_a_blog_post failed",
            exc_info=e,
            extra={
                "post_id": post_id,
            },
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
