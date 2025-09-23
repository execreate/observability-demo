import aiohttp
from core.config import settings
from logging_setup import setup_gunicorn_logging
from schemas import blog_post as blog_post_schemas

logger = setup_gunicorn_logging(__name__)


async def raise_for_status(resp: aiohttp.ClientResponse):
    try:
        resp.raise_for_status()
    except aiohttp.ClientResponseError as err:
        err.message = f"{err.message}: {await resp.text()}"
        raise err


async def create_a_blog_post(body: blog_post_schemas.InBlogPostSchema):
    input_json = body.model_dump()
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{settings.MIRROR_API}/blog",
            json=input_json,
        ) as resp:
            await raise_for_status(resp)
            response_json = await resp.json()
            logger.info(
                f"Mirroring create_a_blog_post success!",
                extra={"input_json": input_json, "response_json": response_json},
            )
            return


async def list_blog_posts(limit: int, offset: int):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{settings.MIRROR_API}/blog",
            params={"limit": limit, "offset": offset},
        ) as resp:
            await raise_for_status(resp)
            response_json = await resp.json()
            logger.info(
                f"Mirroring list_blog_posts success!",
                extra={
                    "limit": limit,
                    "offset": offset,
                    "response_json": response_json,
                },
            )
            return


async def retrieve_a_blog_post(post_id: int):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{settings.MIRROR_API}/blog/{post_id}") as resp:
            await raise_for_status(resp)
            response_json = await resp.json()
            logger.info(
                f"Mirroring retrieve_a_blog_post success!",
                extra={"post_id": post_id, "response_json": response_json},
            )
            return


async def update_a_blog_post(
    post_id: int, body: blog_post_schemas.UpdateBlogPostSchema
):
    input_json = body.model_dump()
    async with aiohttp.ClientSession() as session:
        async with session.patch(
            f"{settings.MIRROR_API}/blog/{post_id}",
            json=body.model_dump(),
        ) as resp:
            await raise_for_status(resp)
            response_json = await resp.json()
            logger.info(
                f"Mirroring update_a_blog_post success!",
                extra={
                    "post_id": post_id,
                    "input_json": input_json,
                    "response_json": response_json,
                },
            )
            return


async def delete_a_blog_post(post_id: int):
    async with aiohttp.ClientSession() as session:
        async with session.delete(f"{settings.MIRROR_API}/blog/{post_id}") as resp:
            await raise_for_status(resp)
            logger.info(
                f"Mirroring delete_a_blog_post success!",
                extra={
                    "post_id": post_id,
                },
            )
            return
