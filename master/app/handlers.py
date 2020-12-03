import asyncio
import logging
import json

from aiohttp import web
from pydantic import ValidationError

from .msg_storage import MsgStorage
from .models import Message, AppendMessage
from .broadcaster import Broadcaster
from .exceptions import WriteConcertError

logger = logging.getLogger(__name__)


class MainHandler:
    def __init__(self, broadcaster: Broadcaster):
        self.msg_storage = MsgStorage()
        self.broadcaster = broadcaster

    async def list_messages(self, request) -> web.Response:
        return web.json_response([msg.dict() for msg in self.msg_storage.get_all()])

    async def append_message(self, request: web.Request) -> web.Response:
        data = await request.json()

        try:
            data = AppendMessage(**data)
        except ValidationError as e:
            return web.json_response(e.json(), status=400)

        msg = Message(message=data.message)
        self.msg_storage.append(msg)

        logger.debug(f"Append message: {{{msg}}} on [MASTER]")

        try:
            await self.broadcaster.broadcast_all_secondaries(msg, data.w)
        except WriteConcertError:
            return web.json_response({'status': 'error', 'msg': 'Write concern error'})

        return web.json_response({'status': 'OK'}, status=400)
