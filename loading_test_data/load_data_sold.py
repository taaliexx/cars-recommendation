import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, select
from models import Dealer, SoldCars  # Импортируем модель
from database import SessionLocal
import numpy as np
import logging 
from globals import CSV_FILE_SALED, DATABASE_URL

logging.basicConfig(level=logging.INFO, 
                    format="%(asctime)s [%(levelname)s] %(message)s")

# Подключение к базе
engine = create_engine(DATABASE_URL)

target_columns = ['manufacturer_name', 'model_name', 'year_produced', 'transmission', 'color', 
                  'odometer_value', 'price_usd', 'previous_owners', 'engine_type', 'body_type']
other_features = ['transmission', 'color', 'previous_owners', 'engine_type', 'body_type']

body_types = ['universal', 'suv', 'sedan', 'hatchback', 'liftback', 'minivan', 'minibus', 'van', 'pickup', 'coupe', 'cabriolet', 'limousine']

colors = ['silver', 'blue', 'red', 'black', 'grey', 'other', 'brown', 'white', 'green', 'violet', 'orange', 'yellow']

def preprocess_data(CSV_FILE: str, seller_name: str):
    df = pd.read_csv(CSV_FILE)
    # Делаем названия полей одинаковыми
    df.rename(columns={'make': 'manufacturer_name', 'model': 'model_name', 'odometer': 'odometer_value', 'sellingprice': 'price_usd', 'year': 'year_produced'}, inplace=True)
    # Удаляем строки с пустыми значениями
    df.dropna(inplace=True)

    df = df[df['seller'] == seller_name]
    
    df = df[df['color'] != '—']

    df['color'] = df['color'].apply(lambda x: 'grey' if x in 'gray' else x)
    df['color'] = df['color'].apply(lambda x: x if x in colors else 'other')
    df['odometer_value'] = df['odometer_value'] * 1.609

    df["previous_owners_num"] = np.random.randint(1, 6, size=len(df))
    df["previous_owners"] = df["previous_owners_num"].apply(lambda x: f'{x}' if x < 4 else 'more than 3')

    df['body'] = df['body'].str.lower()
    df['body'] = df['body'].apply(lambda x: 'coupe' if any(word in x.lower() for word in ['coupe', 'koup']) else x)
    df['body'] = df['body'].apply(lambda x: 'suv' if any(word in x.lower() for word in ['suv']) else x)
    df['body'] = df['body'].apply(lambda x: 'sedan' if any(word in x.lower() for word in ['sedan']) else x)
    df['body'] = df['body'].apply(lambda x: 'pickup' if any(word in x.lower() for word in ['cab']) else x)
    df['body'] = df['body'].apply(lambda x: 'van' if any(word in x.lower() for word in ['van']) else x)
    df['body'] = df['body'].apply(lambda x: 'cabriolet' if any(word in x.lower() for word in ['convertible']) else x)
    df['body'] = df['body'].apply(lambda x: 'universal' if any(word in x.lower() for word in ['wagon']) else x)
    df['body'] = df['body'].apply(lambda x: 'other' if x not in body_types else x)
    df['body_type'] = df['body']

    df["engine_type"] = np.random.choice(['gasoline', 'diesel'], size=len(df))

    df = df[target_columns + ['seller']]

    print(df.head())

    return df

# Функция загрузки данных в БД
def load_csv_to_db(df):
    db: Session = SessionLocal()
    try:
        for _, row in df.iterrows():
            # Получаем dealer_id по имени
            dealer = db.execute(select(Dealer.id).where(Dealer.name == row["seller"])).scalar()

            if not dealer:
                print(f"⚠️ Дилер {row['seller']} не найден, пропускаем запись.")
                continue

            sold_car = SoldCars(
                dealer_id=dealer,
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
            db.add(sold_car)

        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    logging.info(f"Обработка данных")
    cars_sold = preprocess_data(CSV_FILE_SALED, 'kia motors america  inc')
    logging.info(f"Загрузка данных в БД")
    load_csv_to_db(cars_sold)
    logging.info(f"Данные загружены в БД")
