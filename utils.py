from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, status, Request
from globals import SECRET_KEY, ALGORITHM
import pandas as pd
import logging 
from enum import Enum

logging.basicConfig(level=logging.INFO, 
                    format="%(asctime)s [%(levelname)s] %(message)s")

def create_access_token(data: dict, expires_delta: timedelta):
    """Создаёт JWT-токен с истечением времени."""
    to_encode = data.copy()
    expire = datetime.now() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token_from_cookie(request: Request):
    """Извлекает и проверяет JWT токен из куки."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = request.cookies.get("access_token")  # Получаем токен из куки
    if token is None:
        raise credentials_exception
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        dealer_id: str = payload.get("sub")
        if dealer_id is None:
            raise credentials_exception
        return dealer_id
    except JWTError:
        raise credentials_exception

def preprocess_sold_data(df: pd.DataFrame):

    target_columns = ['manufacturer_name', 'model_name', 'year_produced', 'transmission', 'color', 
                  'odometer_value', 'price_usd', 'previous_owners', 'engine_type', 'body_type']
    
    body_types = ['universal', 'suv', 'sedan', 'hatchback', 'liftback', 'minivan', 'minibus', 'van', 'pickup', 'coupe', 'cabriolet', 'limousine']

    colors = ['silver', 'blue', 'red', 'black', 'grey', 'other', 'brown', 'white', 'green', 'violet', 'orange', 'yellow']

    df.dropna(inplace=True)

    df['color'] = df['color'].apply(lambda x: 'grey' if x in 'gray' else x)
    df['color'] = df['color'].apply(lambda x: x if x in colors else 'other')

    df["previous_owners"] = df["previous_owners_num"].apply(lambda x: f'{x}' if x < 4 else 'more than 3')

    df['body_type'] = df['body_type'].str.lower()
    df['body_type'] = df['body_type'].apply(lambda x: 'coupe' if any(word in x.lower() for word in ['coupe', 'koup']) else x)
    df['body_type'] = df['body_type'].apply(lambda x: 'suv' if any(word in x.lower() for word in ['suv']) else x)
    df['body_type'] = df['body_type'].apply(lambda x: 'sedan' if any(word in x.lower() for word in ['sedan']) else x)
    df['body_type'] = df['body_type'].apply(lambda x: 'pickup' if any(word in x.lower() for word in ['cab']) else x)
    df['body_type'] = df['body_type'].apply(lambda x: 'van' if any(word in x.lower() for word in ['van']) else x)
    df['body_type'] = df['body_type'].apply(lambda x: 'cabriolet' if any(word in x.lower() for word in ['convertible']) else x)
    df['body_type'] = df['body_type'].apply(lambda x: 'universal' if any(word in x.lower() for word in ['wagon']) else x)
    df['body_type'] = df['body_type'].apply(lambda x: 'other' if x not in body_types else x)

    df = df[target_columns]

    return df

def detect_separator(content: str):
    """
    Определяет разделитель CSV-файла по его строковому содержимому.
    """
    sample = content[:1024]  # Берем первые 1024 символа
    return ';' if sample.count(';') > sample.count(',') else ','

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