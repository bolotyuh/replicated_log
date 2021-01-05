import os
import pathlib
import sys
from aiohttp import web
import logging
from loguru import logger

from .handlers import MainHandler
from .utils import load_config
from .replication import Replication
from shared.msg_storage import MsgList

PROJ_ROOT = pathlib.Path(__file__).parent.parent

ENV = os.getenv('ENV', 'debug').lower()

config = {
    "handlers": [
        {"sink": sys.stdout, "format": "{level.icon} | {time:YYYY-MM-DD HH:mm:ss} | {message}"},
    ],
}
logger.configure(**config)


def main() -> None:
    logging.basicConfig(level=logging.DEBUG, datefmt='[%H:%M:%S]')

    config_filename = 'config.yml' if ENV == 'debug' else f"config.yml.{ENV}"
    logger.level("HEARTBEAT", no=38, color="<red><bold>", icon="🫀")

    if not os.path.isfile(os.path.join(PROJ_ROOT, config_filename)):
        raise RuntimeError("Config file doesn't exist")

    conf = load_config(os.path.join(PROJ_ROOT, config_filename))
    logger.info(f"Running on {ENV} environment")

    msg_list = MsgList()
    replication = Replication(conf, msg_list)
    handler = MainHandler(replication)

    app = web.Application(logger=logger)
    app.router.add_get("/list-msg", handler.list_messages, name="list_messages")
    app.router.add_post("/append-msg", handler.append_message, name="append_messages")
    web.run_app(app, host=conf['host'], port=conf['port'])
