import logging
from aiohttp import web
from pydantic import ValidationError
import async_timeout
from shared.models import AppendMessage
from .exceptions import WriteConcertError, QuorumException
from .replication import Replication

logger = logging.getLogger(__name__)
FETCH_TIMEOUT = 120


class MainHandler:
    def __init__(self, replication: Replication):
        self.replicator = replication

    async def list_messages(self, request) -> web.Response:
        return web.json_response(self.replicator.msg_list.get_ordered_json())

    async def append_message(self, request: web.Request) -> web.Response:
        data = await request.json()

        try:
            msg = AppendMessage(**data)
        except ValidationError as e:
            return web.json_response(e.json(), status=400)

        with async_timeout.timeout(FETCH_TIMEOUT):
            try:
                await self.replicator.replicate_msg(msg)
            except WriteConcertError:
                return web.json_response({'status': 'error', 'msg': 'Write concern error'}, status=400)
            except QuorumException as e:
                return web.json_response({'status': 'error', 'msg': e.message}, status=400)

            return web.json_response({'status': 'OK'}, status=200)
