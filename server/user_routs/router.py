from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from datetime import datetime
import json

from ..config import templates
from ..config import database
from ..config import logger
from ..config import mqtt
from ..config import SessionData
from ..config import verifier
from ..config import cookie
from ..config import SMOKE_THRESHOLD, GAS_THRESHOLD


router = APIRouter()


@router.get("/device_registration", dependencies=[Depends(cookie)], response_class=HTMLResponse)
async def device_registration(request: Request, session_data: SessionData = Depends(verifier)):
    return templates.TemplateResponse("device_registration.html", {
        "request": request,
        "title": "Регистрация нового девайса",
        **session_data.get_inf()
    })

@router.post("/device_registration_form_process", dependencies=[Depends(cookie)])
async def device_registration_process(
    response: Response,
    mac: str = Form(...),
    room: str = Form(...),
    session_data: SessionData = Depends(verifier)
):
    client_id = session_data.user_id
    
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
        
    return RedirectResponse(url="/user_panel", status_code=303, headers=response.headers)

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

        current_datetime = datetime.now().replace(microsecond=0)
        data_availability = await database.check_data_availability_by_date(device_id, current_datetime)

        if not data_availability:    
            await database.save_data(
                device_id=device_id,
                date=current_datetime,
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


@router.get("/user_panel", dependencies=[Depends(cookie)], response_class=HTMLResponse)
async def user_panel(request: Request, session_data: SessionData = Depends(verifier)):
    client = await database.get_client_by_id(session_data.user_id)
    return templates.TemplateResponse("user_panel.html",
                                        {
                                            'request': request, **session_data.get_inf(),
                                            "title": "Панель пользователя",
                                            'username': client.name
                                        })
