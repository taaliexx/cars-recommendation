# app/schemas.py
from pydantic import BaseModel
from typing import List
from uuid import UUID

class RecommendationBase(BaseModel):
    manufacturer_name: str
    model_name: str
    transmission: str
    year_produced: int
    odometer_value: float
    price_usd: float
    engine_type: str
    body_type: str
    color: str
    previous_owners: str
    distance: float
    predicted_price: float

    class Config:
        orm_mode = True
