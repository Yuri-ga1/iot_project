from pydantic import BaseModel
from typing import List


class RegistrationData(BaseModel):
    mac_address: str
    client_name: str | None
    phone: str


class DeviceData(BaseModel):
    mac_address: str
    smoke_level: float
    gas_level: float
    