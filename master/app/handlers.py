from aiohttp import web
import logging
import json

from .msg_storage import MsgStorage
from .models import Message
from .broadcaster import Broadcaster

logger = logging.getLogger(__name__)


class MainHandler:
    def __init__(self, broadcaster: Broadcaster):
        self.msg_storage = MsgStorage()
        self.broadcaster = broadcaster

    async def list_messages(self, request) -> web.Response:
        return web.json_response([msg.dict() for msg in self.msg_storage.get_all()])

    async def append_message(self, request: web.Request) -> web.Response:
        data = await request.json()
        msg = Message(**data)
        self.msg_storage.append(msg)

        logger.debug(f"Append message: {msg}")

        await self.broadcaster.broadcast_all_secondaries(msg)

        return web.json_response({'status': 'OK'})
