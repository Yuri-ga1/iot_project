#html странички
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="server/templates")

#База данных
from .database_module.database import Database

database = Database()

#создание mqtt
from fastapi_mqtt import FastMQTT, MQTTConfig

mqtt_config = MQTTConfig(
    host="broker.emqx.io",
    port=1883,
    keepalive=60
)
mqtt = FastMQTT(config=mqtt_config)

#логирование
import logging

logging.basicConfig(
    level=logging.INFO,
    datefmt="%m/%d/%Y %I:%M:%S",
    filename="logs.log",
    filemode="a",
    format="%(asctime)s : %(levelname)s : %(message)s",
)

logger = logging.getLogger()


#инициализация основного приложения
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def _lifespan(_app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()

app = FastAPI(lifespan=_lifespan)
mqtt.init_app(app)
