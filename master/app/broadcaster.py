import asyncio
import logging
from typing import List, Dict
from collections import namedtuple
from aiohttp import ClientSession, ClientConnectorError

from .models import Message

logger = logging.getLogger(__name__)

Secondary = namedtuple('Secondary', ['name', 'url'])

BROADCAST_STATUS_FAILED = "failed"
BROADCAST_STATUS_SUCCESS = "OK"


class Broadcaster:
    def __init__(self, conf: Dict):
        self.secondaries: List[Secondary] = [Secondary(**sec) for sec in conf['secondaries']]

    async def broadcast_all_secondaries(self, msg: Message):
        tasks = [self._get_task_for_notify(msg, secondary) for secondary in self.secondaries]

        for task in asyncio.as_completed(tasks):
            try:
                res: Dict = await task
            except Exception as e:
                logger.exception(e)
            else:
                if res.get('ack') == BROADCAST_STATUS_FAILED:
                    logger.info(f'Failed to replicate message on the node "{res.get("name")}"')
                elif res.get('ack') == BROADCAST_STATUS_SUCCESS:
                    logger.info(f'Success to replicate message on the node "{res.get("name")}"')

    async def _get_task_for_notify(self, msg: Message, secondary: Secondary) -> Dict:
        res: Dict = {'acknowledgment': BROADCAST_STATUS_FAILED}

        async with ClientSession() as client:
            try:
                ws = await client.ws_connect(secondary.url)
                await ws.send_json(msg.dict())
            except ClientConnectorError:
                logger.exception(f'Failure connection on the node "{secondary.name}"')
            else:
                res.update(await ws.receive_json())

            res['name'] = secondary.name

        return res
