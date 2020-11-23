import asyncio
from aiohttp import web
import logging

from .msg_storage import MsgStorage
from .models import Message

logger = logging.getLogger(__name__)


class MainHandler:
    def __init__(self):
        self.msg_storage = MsgStorage()

    async def list_messages(self, request):
        return web.json_response([msg.dict() for msg in self.msg_storage.get_all()])

    async def ws_append_message(self, request: web.Request, delay=0) -> None:
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        data = await ws.receive_json()
        logger.info(f'Receive a message on node {data}')

        if type(delay) == int:
            logger.debug(f'User delay: {delay}')
            await asyncio.sleep(delay)

        self.msg_storage.append(Message(**data))
        await ws.send_json({'ack': 'OK'})
        await ws.close()
