import os
import pathlib
from aiohttp import web
import logging

from .handlers import MainHandler
from .utils import load_config
from .broadcaster import Broadcaster

PROJ_ROOT = pathlib.Path(__file__).parent.parent
logger = logging.getLogger(__name__)
LOGGER_FORMAT = '%(asctime)s %(message)s'
ENV = os.getenv('ENV', 'debug').lower()


def main() -> None:
    logging.basicConfig(level=logging.DEBUG, format=LOGGER_FORMAT, datefmt='[%H:%M:%S]')

    config_filename = 'config.yml' if ENV == 'debug' else f"config.yml.{ENV}"

    if not os.path.isfile(os.path.join(PROJ_ROOT, config_filename)):
        raise RuntimeError("Config file doesn't exist")

    conf = load_config(os.path.join(PROJ_ROOT, config_filename))
    logger.info(f"Running on {ENV} environment")

    broadcaster = Broadcaster(conf)
    handler = MainHandler(broadcaster)

    app = web.Application(logger=logger)
    app.router.add_get("/list-msg", handler.list_messages, name="list_messages")
    app.router.add_post("/append-msg", handler.append_message, name="append_messages")
    web.run_app(app, host=conf['host'], port=conf['port'])
