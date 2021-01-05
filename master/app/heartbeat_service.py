import json
import asyncio
from urllib.parse import urljoin
from aiohttp import (
    ClientSession,
    ClientConnectorError,
    ClientTimeout
)
from typing import NoReturn
from loguru import logger


def log_heartbeat(node: "NodeSecondary") -> NoReturn:
    labels = {
        HeartbeatService.STATUS_UNKNOWN: "<bold><white>UNKNOWN</white></bold>",
        HeartbeatService.STATUS_HEALTHY: "<bold><green>HEALTHY</green></bold>",
        HeartbeatService.STATUS_UNHEALTHY: "<bold><red>UNHEALTHY</red></bold>",
        HeartbeatService.STATUS_SUSPECTED: "<bold><white>SUSPECTED</white></bold>",
    }

    logger.opt(colors=True).log("HEARTBEAT", f"node: <bold>{node.name.ljust(15)}</bold> [{labels[node.status]}]")


class HeartbeatService:
    STATUS_UNKNOWN = 'unknown'
    STATUS_HEALTHY = 'healthy'
    STATUS_SUSPECTED = 'suspected'
    STATUS_UNHEALTHY = 'unhealthy'

    TRANSITIONS = {
        STATUS_UNHEALTHY: STATUS_UNHEALTHY,
        STATUS_UNKNOWN: STATUS_UNHEALTHY,
        STATUS_HEALTHY: STATUS_SUSPECTED,
        STATUS_SUSPECTED: STATUS_UNHEALTHY
    }

    def __init__(self, delay: int = 5, timeout: float = 10.0):
        self.delay = delay
        heartbeat_timeout = ClientTimeout(total=timeout)
        self.session = ClientSession(timeout=heartbeat_timeout)

    async def heartbeat_node(self, node: "NodeSecondary"):

        while True:
            try:
                async with self.session.get(urljoin(node.url, 'health')) as response:
                    resp = await response.text()
                    resp_json = json.loads(resp)
                    node.status = resp_json['status']
            except ClientConnectorError as error:
                node.status = HeartbeatService.TRANSITIONS[node.status]
            finally:
                log_heartbeat(node)
                await asyncio.sleep(self.delay)
