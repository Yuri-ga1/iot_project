from pydantic import BaseModel


class DeviceData(BaseModel):
    mac_address: str
    smoke_level: float
    gas_level: float
    