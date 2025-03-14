# app/schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import List
from uuid import UUID
from enum import Enum

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

class DealerInfo(BaseModel):
    name: str
    email: str
    created_at: datetime  # datetime type will automatically be serialized to ISO format

    class Config:
        orm_mode = True

class TransmissionEnum(str, Enum):
    automatic = "automatic"
    manual = "manual"

class EngineTypeEnum(str, Enum):
    gasoline = "gasoline"
    diesel = "diesel"

class BodyTypeEnum(str, Enum):
    universal = "universal"
    suv = "suv"
    sedan = "sedan"
    hatchback = "hatchback"
    liftback = "liftback"
    minivan = "minivan"
    minibus = "minibus"
    van = "van"
    pickup = "pickup"
    coupe = "coupe"
    cabriolet = "cabriolet"
    limousine = "limousine"
    other = "other"

class ColorEnum(str, Enum):
    silver = "silver"
    blue = "blue"
    red = "red"
    black = "black"
    grey = "grey"
    brown = "brown"
    white = "white"
    green = "green"
    violet = "violet"
    orange = "orange"
    yellow = "yellow"
    other = "other"

class PreviousOwnersEnum(str, Enum):
    one = "1"
    two = "2"
    three = "3"
    more_than_three = "more than 3"

class Car(BaseModel):
    manufacturer_name: str
    model_name: str
    transmission: TransmissionEnum
    year_produced: int
    odometer_value: float
    price_usd: float
    engine_type: EngineTypeEnum
    body_type: BodyTypeEnum
    color: ColorEnum
    previous_owners: PreviousOwnersEnum