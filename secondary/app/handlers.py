import asyncio
from aiohttp import web
from loguru import logger
import random

from shared.msg_storage import MsgList
from shared.models import Message


class MainHandler:
    def __init__(self, delay: int, error_prob: float):
        self.msg_storage = MsgList()
        self.delay = delay
        self.error_prob = error_prob

    async def health(self, request):
        return web.json_response({"status": "healthy"})

    async def list_messages(self, request):
        return web.json_response(self.msg_storage.get_ordered_json())

    async def append_message(self, request: web.Request) -> web.Response:
        if random.random() < self.error_prob:
            logger.opt(colors=True).info("<bold><red>Emulate Internal server error</red></bold>")
            return web.json_response({"status": "internal server error"}, status=500)

        # emulate delay
        if int(self.delay) > 0:
            delay = random.random() * 10
            logger.opt(colors=True).info(f"<bold><red>Emulate delay: {delay:.4}</red></bold>")
            await asyncio.sleep(delay)

        data = await request.json()
        logger.opt(colors=True).info(f'<yellow>Receive a message on node {data}</yellow>')

        self.msg_storage.append(Message(**data))

        logger.opt(colors=True).info(f'<yellow>Append a message on node {data}</yellow>')
        return web.json_response({'ack': 'OK'})
