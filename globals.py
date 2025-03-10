CSV_FILE_FOR_SALE = 'cars.csv'
CSV_FILE_SALED = "car_prices.csv"
USERNAME = 'USERNAME'
PASSWORD = 'PASSWORD'
DB_NAME = 'DB_NAME'
DATABASE_URL = f'postgresql://{USERNAME}:{PASSWORD}@localhost/{DB_NAME}'

# Настройки JWT
from dotenv import load_dotenv
import os
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 90 