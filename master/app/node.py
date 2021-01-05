import asyncio
import random
from typing import Any, Dict
from aiohttp import ClientSession, ClientConnectorError
from urllib.parse import urljoin
from loguru import logger

from .heartbeat_service import HeartbeatService
from shared.models import Message

BROADCAST_STATUS_FAILED = "failed"
BROADCAST_STATUS_SUCCESS = "OK"


class NodeSecondary:
    def __init__(self, url, name):
        self.status: str = HeartbeatService.STATUS_UNKNOWN
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.future: Any = None
        self.name = name
        self.url = url
        self.retry_attempts: int = 0
        self.retry_delay = random.random() * 5
        heartbeat = HeartbeatService()
        asyncio.ensure_future(heartbeat.heartbeat_node(self))

    async def _send_msg(self, msg: Message) -> Dict:
        res: Dict = {'acknowledgment': BROADCAST_STATUS_FAILED}
        async with ClientSession() as client:
            try:
                async with client.post(urljoin(self.url, 'append-msg'), json=msg.dict()) as resp:
                    res.update(await resp.json())
            except ClientConnectorError as e:
                # logger.error(f'Failure connection on the node [{self.name}]')
                raise e

            res['name'] = self.name

        return res

    async def process(self):
        while not self.message_queue.empty():
            qmsg = self.message_queue.get_nowait()

            try:
                await self._send_msg(qmsg)
            except ClientConnectorError:
                self.retry_attempts += 1

                if self.retry_attempts % 5 == 0:
                    self.retry_delay += 2

                await asyncio.sleep(self.retry_delay)
                logger.opt(colors=True).info(
                    f'<red>Retry send message `{qmsg.id}` on node [{self.name}], attempts [{self.retry_attempts}], delay [{self.retry_delay:.4}]</red>')
                self.message_queue.put_nowait(qmsg)
            else:
                logger.opt(colors=True).info(f'<green>Successful sent message `{qmsg.id}` on node [{self.name}]</green>')
                self.retry_attempts = 0
