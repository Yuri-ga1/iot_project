from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="server/templates")

#База данных
from .database_module.database import Database

database = Database()

# Пороговые значения для газа и дыма

SMOKE_THRESHOLD = 300
GAS_THRESHOLD = 500

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


# mqtt
from fastapi_mqtt import FastMQTT, MQTTConfig

mqtt_config = MQTTConfig(
    host="broker.emqx.io",
    port=1883,
    keepalive=60
)
mqtt = FastMQTT(config=mqtt_config)

#инициализация приложения
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
        if macs:
            for mac in macs:
                mac = mac[0]
                try:
                    logger.info(f"Resubscribing on topic: detectors/{mac}")
                    mqtt.client.subscribe(f"detectors/{mac}")
                except:
                    logger.error(f"Failed to resubscribing on topic: detectors/{mac}")
                    
        
# Сессии
from uuid import UUID
from .user_routs.schemas import SessionData
from fastapi_sessions.backends.implementations import InMemoryBackend
from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters
from fastapi_sessions.session_verifier import SessionVerifier
from fastapi import HTTPException


backend = InMemoryBackend[UUID, SessionData]()
cookie_params = CookieParameters(httponly=False)

cookie = SessionCookie(
    cookie_name="cookie",
    identifier="general_verifier",
    auto_error=True,
    secret_key="DONOTUSE",
    cookie_params=cookie_params,
)

class BasicVerifier(SessionVerifier[UUID, SessionData]):
    def __init__(
        self,
        *,
        identifier: str,
        auto_error: bool,
        backend: InMemoryBackend[UUID, SessionData],
        auth_http_exception: HTTPException,
    ):
        self._identifier = identifier
        self._auto_error = auto_error
        self._backend = backend
        self._auth_http_exception = auth_http_exception

    @property
    def identifier(self):
        return self._identifier

    @property
    def backend(self):
        return self._backend

    @property
    def auto_error(self):
        return self._auto_error

    @property
    def auth_http_exception(self):
        return self._auth_http_exception

    def verify_session(self, model: SessionData) -> bool:
        """If the session exists, it is valid"""
        return True

verifier = BasicVerifier(
    identifier="general_verifier",
    auto_error=True,
    backend=backend,
    auth_http_exception=HTTPException(status_code=403, detail="invalid session"),
)
