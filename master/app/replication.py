from __future__ import annotations
import asyncio
import time
from loguru import logger
from collections import namedtuple
from typing import List, Dict

from ._tasks import wait_n
from .node import NodeSecondary
from .heartbeat_service import HeartbeatService
from .exceptions import WriteConcertError, QuorumException
from shared.models import AppendMessage, Message
from shared.msg_storage import MsgList

Secondary = namedtuple('Secondary', ['name', 'url'])


class Replication:
    def __init__(self, conf: Dict, msg_list: MsgList):
        self.msg_list = msg_list
        self.nodes: List[NodeSecondary] = []

        for sec in [Secondary(**sec) for sec in conf['secondaries']]:
            self.__add_node(sec.url, sec.name)

    def get_count_of_live_nodes(self):
        return len([1 for node in self.nodes if node.status == HeartbeatService.STATUS_HEALTHY])

    def calc_quorum(self):
        return len(self.nodes) // 2 + 1

    def check_quorum(self):
        live_node_count = self.get_count_of_live_nodes() + 1
        return live_node_count < self.calc_quorum()

    def __add_node(self, url, name) -> Replication:
        logger.info(f'Add node "{name}"')

        node = NodeSecondary(url, name)
        self.nodes.append(node)

        return self

    def _push_message(self, message):
        for node in self.nodes:
            node.message_queue.put_nowait(message)

    async def _handle_unfinished_tasks(self, fs):
        for f in asyncio.as_completed(fs):
            await f

    async def replicate_msg(self, data: AppendMessage):
        write_concern = data.w

        # override can`t be bigger than count nodes
        write_concern = write_concern if write_concern <= len(self.nodes) else len(self.nodes)
        logger.info(f'Running with write concert "{write_concern}"')

        if self.check_quorum():
            error_message = f'Not enough nodes in quorum, only {self.get_count_of_live_nodes()} nodes alive'
            raise QuorumException(message=error_message)

        msg = Message(
            message=data.message,
            id=int(time.time() * 1000.0),
            order=self.msg_list.count()
        )
        self.msg_list.append(msg)
        logger.debug(f"Append message: {{{msg}}} on [MASTER]")

        self._push_message(msg)

        tasks = [node.process() for node in self.nodes]
        n_of_confirmed_task = 0

        done, pending = await wait_n(tasks, n=write_concern)

        for task in done:
            try:
                await task
            except Exception as e:
                logger.exception(e)
            else:
                n_of_confirmed_task += 1

        if n_of_confirmed_task < write_concern:
            raise WriteConcertError

        asyncio.create_task(self._handle_unfinished_tasks(pending))
