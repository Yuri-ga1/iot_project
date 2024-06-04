from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import hashlib
from datetime import datetime
import json

from ..config import templates
from ..config import database
from ..config import logger
from ..config import mqtt


router = APIRouter()


@router.get("/user_registration", response_class=HTMLResponse)
async def registration(request: Request):
    return templates.TemplateResponse("user_registration.html", {"request": request, "title": "Регистрация нового пользователя"})

@router.post("/user_registration_form_process")
async def registration(
    name: str = Form(...),
    login: str = Form(...),
    password: str = Form(...),
    email: str = Form(...)
    ):
    hashed_password = await hash_password(password)
    client_id = await database.get_client(login, hashed_password)
        
    if client_id is None:
        await database.add_client(
            name=name,
            login=login,
            password=hashed_password,
            email=email
        )
        
    return RedirectResponse(url="/", status_code=303)


@router.get("/device_registration", response_class=HTMLResponse)
async def registration(request: Request):
    return templates.TemplateResponse("device_registration.html", {"request": request, "title": "Регистрация нового девайса"})


@router.post("/device_registration_form_process")
async def device_registration(
    login: str = Form(...),
    password: str = Form(...),
    mac: str = Form(...),
    room: str = Form(...)
):
    hashed_password = await hash_password(password)
    client_id = await database.get_client(login, hashed_password)
    if client_id is None:
        return RedirectResponse(url="user_registration", status_code=303)
    
    device_id = await database.get_device_by_mac(mac)
    
    if device_id is None:
        await database.add_device(
            mac=mac,
            room=room,
            client_id=client_id
        )
        logger.info(f"Device with MAC: {mac} registered successfully")
        
    if mqtt.client.is_connected:
        mqtt.client.subscribe(f"detectors/{mac}")
        logger.info(f"Subscribed to MQTT topic: detectors/{mac}")
    else:
        logger.error("Failed to subscribe to MQTT topic: MQTT client is not connected")
        
    return RedirectResponse(url="/", status_code=303)


@mqtt.on_connect()
def connect(client, flags, rc, properties):
    logger.info(f"Connected to MQTT Broker: {client}, Flags: {flags}, RC: {rc}, Properties: {properties}")

@mqtt.on_message()
async def message(client, topic, payload, qos, properties):
    try:
        payload = json.loads(payload.decode("utf-8"))
        mac_address = payload.get("mac_address")
        smoke_level = payload.get("smoke_level")
        gas_level = payload.get("gas_level")
        
        if gas_level == 0:
            return
    
        device_id = await database.get_device_by_mac(mac_address)
    
        await database.save_data(
            device_id=device_id,
            date= datetime.now(),
            smoke_level=smoke_level,
            gas_level=gas_level
        )
    except json.JSONDecodeError:
        logger.warning("Received non-JSON message")

@mqtt.on_disconnect()
def disconnect(client, packet, exc=None):
    logger.warning("Disconnected from MQTT Broker")

@mqtt.on_subscribe()
def subscribe(client, mid, qos, properties):
    logger.info(f"Subscribed: {client}, MID: {mid}, QoS: {qos}, Properties: {properties}")


async def hash_password(password: str) -> str:
    md5_hash = hashlib.md5()
    md5_hash.update(password.encode('utf-8'))
    return md5_hash.hexdigest()
    