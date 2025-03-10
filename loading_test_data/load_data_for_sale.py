import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from models import CarsForSale
from database import SessionLocal
import numpy as np
import logging 
from globals import CSV_FILE_FOR_SALE, DATABASE_URL

logging.basicConfig(level=logging.INFO, 
                    format="%(asctime)s [%(levelname)s] %(message)s")

# Подключение к базе
engine = create_engine(DATABASE_URL)

target_columns = ['manufacturer_name', 'model_name', 'year_produced', 'transmission', 'color', 
                  'odometer_value', 'price_usd', 'previous_owners', 'engine_type', 'body_type']
other_features = ['transmission', 'color', 'previous_owners', 'engine_type', 'body_type']

def preprocess_data(CSV_FILE: str):
    df = pd.read_csv(CSV_FILE)
    # Удаляем строки с пустыми значениями
    df.dropna(inplace=True)

    df['transmission'] = df['transmission'].str.replace('mechanical', 'manual')

    df["previous_owners_num"] = np.random.randint(1, 6, size=len(df))
    df["previous_owners"] = df["previous_owners_num"].apply(lambda x: f'{x}' if x < 4 else 'more than 3')
    df = df[target_columns]

    return df

# Функция загрузки данных в БД
def load_csv_to_db(df: pd.DataFrame):
    db: Session = SessionLocal()
    try:
        for _, row in df.iterrows():
            car = CarsForSale(
                manufacturer_name=row["manufacturer_name"],
                model_name=row["model_name"],
                transmission=row["transmission"],
                year_produced=row["year_produced"],
                odometer_value=row["odometer_value"],
                price_usd=row["price_usd"],
                engine_type=row["engine_type"],
                body_type=row["body_type"],
                color=row["color"],
                previous_owners=row["previous_owners"]
            )
            db.add(car)
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    logging.info(f"Обработка данных")
    cars_for_sale = preprocess_data(CSV_FILE_FOR_SALE)
    logging.info(f"Загрузка данных в БД")
    load_csv_to_db(cars_for_sale)
    logging.info(f"Данные загружены в БД")
