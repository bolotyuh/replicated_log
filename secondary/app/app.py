import sys
from typing import Any
from aiohttp import web
import logging
from loguru import logger

from .handlers import MainHandler

config = {
    "handlers": [
        {"sink": sys.stdout, "format": "{level.icon} | {time:YYYY-MM-DD HH:mm:ss} | {message}"},
    ],
}
logger.configure(**config)


def main(args: Any = None) -> None:
    handler = MainHandler(args.delay, args.error_prob)
    logging.basicConfig(level=logging.INFO, datefmt='[%H:%M:%S]')

    app = web.Application(logger=logger)
    app.router.add_get("/list-msg", handler.list_messages, name="list_messages")
    app.router.add_get("/health", handler.health, name="health")

    app.router.add_post("/append-msg", handler.append_message, name="append_messages")

    web.run_app(app, host=args.host, port=args.port)
