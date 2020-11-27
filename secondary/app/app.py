from typing import Any
from aiohttp import web
import logging
from functools import partial

from .handlers import MainHandler

logger = logging.getLogger(__name__)
LOGGER_FORMAT = '%(asctime)s %(message)s'


def main(args: Any = None) -> None:
    handler = MainHandler()
    logging.basicConfig(level=logging.DEBUG, format=LOGGER_FORMAT, datefmt='[%H:%M:%S]')

    app = web.Application(logger=logger)
    app.router.add_get("/list-msg", handler.list_messages, name="list_messages")

    ws_append_handler = partial(handler.ws_append_message, delay=args.delay)
    app.router.add_get("/ws-append-msg", ws_append_handler, name="append_messages")

    web.run_app(app, host=args.host, port=args.port)
