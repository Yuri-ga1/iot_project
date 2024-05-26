from fastapi import APIRouter, HTTPException
from .schemas import *
from ..database_module.database import database
import phonenumbers
from phonenumbers import NumberParseException
from datetime import datetime



router = APIRouter()


@router.post("/registration")
async def registration(registration_data: RegistrationData):
    phone = registration_data.phone
    if await is_valid_phone_number(phone):
        client_id = await database.get_client_by_phone(phone)
        
        if client_id is None:
            await database.add_client(
                name=registration_data.client_name,
                phone=registration_data.phone
            )
            client_id = await database.get_client_by_phone(phone)
 
        await database.add_device(
            mac=registration_data.mac_address,
            client_id=client_id
        )
        return {"message": "You have successfully registered your device"}
    return {"message": "Invalid phone number"}


@router.post("/post_data")
async def registration(data: DeviceData):
    device_id = await database.get_device_by_mac(data.mac_address)
    
    if device_id is None:
        raise HTTPException(404, "Device is not registered")
    
    await database.save_data(
        device_id=device_id,
        date= datetime.now(),
        smoke_level=data.smoke_level,
        gas_level=data.gas_level
    )
    
       
async def is_valid_phone_number(phone):
    try:
        parsed_number = phonenumbers.parse(phone, None)
        return phonenumbers.is_valid_number(parsed_number)
    except NumberParseException:
        return False
        