from sklearn.neighbors import NearestNeighbors
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from models import CarsForSale, SoldCars, Dealer, Recommendations
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge
import uuid
from datetime import datetime
from preprocessing import preprocess_data

import logging 

logging.basicConfig(level=logging.INFO, 
                    format="%(asctime)s [%(levelname)s] %(message)s")

def get_knn_recommendations(dealer_id: str, db: Session):
    
    # Загружаем данные о проданных и выставленных на продажу автомобилях
    dealer_id = uuid.UUID(dealer_id)  # Например, UUID дилера
    sold_cars_db = db.query(SoldCars).filter(SoldCars.dealer_id == dealer_id).all()
    cars_for_sale_db = db.query(CarsForSale).all()
    
    saled_cars, cars_for_sale = preprocess_data(sold_cars_db, cars_for_sale_db)

    def train_regression_for_dealer(saled_cars):
        """Обучает регрессию на данных конкретного дилера"""
        dealer_sales = saled_cars
        
        if dealer_sales.shape[0] < 20:  # Минимум данных для обучения
            print(f"Недостаточно данных для обучения модели регрессии для дилера {dealer_id}")
            return None

        X_train = np.vstack(dealer_sales['full_vector'].values)
        y_train = dealer_sales['price_usd']

        model = Pipeline([
            ('scaler', StandardScaler()),
            ('regressor', Ridge(alpha=1.0))
        ])
        model.fit(X_train, y_train)
        
        return model

    # 1. Обучаем модель регрессии для данного дилера
    model = train_regression_for_dealer(saled_cars)
    if model is None:
        print(f"Недостаточно данных для построения рекомендаций для {dealer_id}")
        return None
    
    # 2. Формируем вектор признаков для машин, которые были проданы этим дилером
    sold_cars_by_dealer_vector = saled_cars['full_vector']

    # 3. Формируем вектор признаков для всех машин на продаже
    cars_for_sale_vector = cars_for_sale['full_vector']

    # 4. Вычисляем сходство между машинами на продаже и проданными машинами данного дилера
    X_sold = np.vstack(sold_cars_by_dealer_vector)
    X_for_sale = np.vstack(cars_for_sale_vector)

    # 6. Используем KNN для поиска ближайших машин
    knn = NearestNeighbors(n_neighbors=5, metric='cosine')
    knn.fit(X_for_sale)

    # 7. Для каждой проданной машины дилера находим ближайших соседей среди машин на продаже
    recommendations = []

    for sold_vector in X_sold:
        distances, indices = knn.kneighbors([sold_vector])

        # Сортируем рекомендации по расстоянию (ближайшие будут первыми)
        recommended_cars = cars_for_sale.iloc[indices[0]].copy()
        recommended_cars['distance'] = distances[0]  # Добавляем расстояние для сортировки
        
        X_pred_price = recommended_cars.apply(
            lambda x: np.concatenate([
                x['full_car_name_embedding'],
                x['transmission_embedding'],
                x['colors_embedding'],
                x['previous_owners_embedding'],
                x['engine_type_embedding'],
                x['body_type_embedding'],
                np.array([x['price_usd_scaled_mm']]),  # Преобразуем число в одномерный массив
                np.array([x['odometer_value_scaled_mm']]),  # Преобразуем число в одномерный массив
                np.array([x['year_produced_scaled_mm']]),
            ]), axis=1
        )
        X_pred_price = np.vstack(X_pred_price)

        recommended_cars['predicted_price'] = model.predict(X_pred_price)
        # recommended_cars['profit'] = recommended_cars['predicted_price'] - recommended_cars['price_usd']

        # Сортируем по расстоянию
        recommended_cars = recommended_cars.sort_values(by=['distance'], ascending=[True])
        
        recommendations.append(recommended_cars)

    # 8. Сливаем все рекомендованные машины
    recommended_cars_all = pd.concat(recommendations)
 
    recommended_cars_all = recommended_cars_all.sort_values(by=['distance'], ascending=[True])

    logging.info(f'{recommended_cars_all.head(5)}')

    # recommendations_dict = recommended_cars_all.to_dict(orient='records')

    return recommended_cars_all


from sqlalchemy.orm import Session
from models import Recommendations
import uuid

def save_recommendations_to_db(recommendations, dealer_id: uuid.UUID, db: Session):
    """
    Сохраняет рекомендации в базу данных.

    recommendations: list[dict] -> список рекомендованных автомобилей (из to_dict).
    dealer_id: UUID -> ID дилера, которому выдаются рекомендации.
    db: Session -> сессия SQLAlchemy.
    """
    for rec in recommendations:
        # Получаем UUID автомобиля по индексу
        car_uuid = db.query(CarsForSale.id).filter(CarsForSale.id == rec["id"]).scalar()

        if car_uuid is None:
            continue  # Если не нашли, пропускаем

        db.add(Recommendations(
            dealer_id=dealer_id,
            recommended_car_id=car_uuid,
            distance=float(rec["distance"]),
            predicted_price=float(rec["predicted_price"]),
            profit=float(rec["predicted_price"]) - float(rec["price_usd"]),
            created_at=datetime.now().isoformat()
        ))

    db.commit()

