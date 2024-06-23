from pydantic import BaseModel

class EnergyReading(BaseModel):
    device_id: str
    timestamp: str
    consumption: float

class Device(BaseModel):
    id: str
    name: str
    status: str