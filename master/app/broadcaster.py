import asyncio
import logging
from typing import List, Dict
from collections import namedtuple
from aiohttp import ClientSession, ClientConnectorError

from .models import Message
from ._tasks import wait_n
from .exceptions import WriteConcertError

logger = logging.getLogger(__name__)

Secondary = namedtuple('Secondary', ['name', 'url'])

BROADCAST_STATUS_FAILED = "failed"
BROADCAST_STATUS_SUCCESS = "OK"


class Broadcaster:
    def __init__(self, conf: Dict):
        self.secondaries: List[Secondary] = [Secondary(**sec) for sec in conf['secondaries']]

    async def broadcast_all_secondaries(self, msg: Message, write_concern: int = 1):
        tasks = [self._get_task_for_notify(msg, secondary) for secondary in self.secondaries]
        n_of_confirmed_task = 0

        logger.info(f'Running with write concert "{write_concern}"')

        done, pending = await wait_n(tasks, n=write_concern)

        for task in done:
            try:
                await self.process_task(task)
            except Exception as e:
                logger.exception(e)
            else:
                n_of_confirmed_task += 1

        if n_of_confirmed_task < write_concern:
            raise WriteConcertError

        asyncio.create_task(self._handle_unfinished_tasks(pending))

    async def process_task(self, t):
        try:
            res: Dict = await t
        except Exception:
            raise
        else:
            if res.get('ack') == BROADCAST_STATUS_FAILED:
                logger.info(f'Failed to replicate message on the node [{res.get("name")}]')
            elif res.get('ack') == BROADCAST_STATUS_SUCCESS:
                logger.info(f'Success to replicate message on the node [{res.get("name")}]')

    async def _handle_unfinished_tasks(self, fs):
        for f in asyncio.as_completed(fs):
            await self.process_task(f)

    async def _get_task_for_notify(self, msg: Message, secondary: Secondary) -> Dict:
        res: Dict = {'acknowledgment': BROADCAST_STATUS_FAILED}

        async with ClientSession() as client:
            try:
                ws = await client.ws_connect(secondary.url)
                await ws.send_json(msg.dict())
            except ClientConnectorError as e:
                logger.error(f'Failure connection on the node [{secondary.name}]')
                raise e
            else:
                res.update(await ws.receive_json())

            res['name'] = secondary.name

        return res
