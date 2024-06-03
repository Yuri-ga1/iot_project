from fastapi import APIRouter, HTTPException
from .schemas import *
from datetime import datetime

from ..config import database

router = APIRouter()


@router.post("/post_data")
async def registration(data: DeviceData):
    if data.gas_level == 0:
        return
    
    device_id = await database.get_device_by_mac(data.mac_address)
    
    if device_id is None:
        raise HTTPException(404, "Device is not registered")
    
    await database.save_data(
        device_id=device_id,
        date= datetime.now(),
        smoke_level=data.smoke_level,
        gas_level=data.gas_level
    )
        