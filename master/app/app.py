import os
import pathlib
from aiohttp import web
import logging

from .handlers import MainHandler
from .utils import load_config
from .broadcaster import Broadcaster

PROJ_ROOT = pathlib.Path(__file__).parent.parent
logger = logging.getLogger(__name__)


def main() -> None:
    conf = load_config(os.path.join(PROJ_ROOT, 'config.yml'))

    logging.basicConfig(level=logging.DEBUG)
    broadcaster = Broadcaster(conf)
    handler = MainHandler(broadcaster)

    app = web.Application(logger=logger)
    app.router.add_get("/list-msg", handler.list_messages, name="list_messages")
    app.router.add_post("/append-msg", handler.append_message, name="append_messages")
    web.run_app(app, host=conf['host'], port=conf['port'])
