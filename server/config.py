#html странички
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="server/templates")

#База данных
from .database_module.database import Database

database = Database()

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


#создание mqtt
from fastapi_mqtt import FastMQTT, MQTTConfig

mqtt_config = MQTTConfig(
    host="broker.emqx.io",
    port=1883,
    keepalive=60
)
mqtt = FastMQTT(config=mqtt_config)

#инициализация основного приложения
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def _lifespan(_app: FastAPI):
    await database.connect()
    await mqtt.mqtt_startup()
    await topic_resubscribe()
    yield
    await mqtt.mqtt_shutdown()
    await database.disconnect()

app = FastAPI(lifespan=_lifespan)


async def topic_resubscribe():
    if mqtt.client.is_connected:
        macs = await database.get_devices_mac()
        for mac in macs:
            mac = mac[0]
            try:
                logger.info(f"Resubscribing on topic: detectors/{mac}")
                mqtt.client.subscribe(f"detectors/{mac}")
            except:
                logger.error(f"Failed to resubscribing on topic: detectors/{mac}")
                    
        
