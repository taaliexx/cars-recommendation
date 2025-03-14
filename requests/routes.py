from fastapi import Depends, APIRouter, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Dealer, CarsForSale, SoldCars, Recommendations
from typing import List
from recommendations import get_knn_recommendations, save_recommendations_to_db
from schemas import RecommendationBase, DealerInfo, Car
import uuid
import logging 
import pandas as pd
import io
from utils import verify_token_from_cookie, preprocess_sold_data, EngineTypeEnum, ColorEnum, BodyTypeEnum, TransmissionEnum, PreviousOwnersEnum, detect_separator

router = APIRouter(prefix="", tags=["requests"])

@router.get("/cars_for_sale", response_model=List[dict])
def get_cars_for_sale(db: Session = Depends(get_db)):
    """
    Cписок всех машин, которые можно приобрести для дальнейшей продажи.
    """
    cars_for_sale = db.query(CarsForSale).limit(1000).all()
    return [{"id": str(car.id), 
             "manufacturer_name": car.manufacturer_name, 
             "model": car.model_name,
             "year_produced": car.year_produced,
             "odometer_value": car.odometer_value,
             "previous_owners": car.previous_owners,
             "color": car.color,
             "transmission": car.transmission,
             "engine_type": car.engine_type,
             "body_type": car.body_type,
             "price_usd": car.price_usd} for car in cars_for_sale]

@router.get("/dealer_info", response_model=DealerInfo)
def get_dealer_info(dealer_id: str = Depends(verify_token_from_cookie), db: Session = Depends(get_db)):
    """
    Получить информацию о дилере
    """
    dealer_id = uuid.UUID(dealer_id)
    dealer = db.query(Dealer).filter(Dealer.id == dealer_id).first()
    
    if not dealer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dealer not found"
        )
    
    return dealer

@router.get("/dealers_cars", response_model=List[dict])
def get_dealers_cars(dealer_id: str = Depends(verify_token_from_cookie), db: Session = Depends(get_db)):
    """
    Информация о дилере
    """
    dealer_id = uuid.UUID(dealer_id)
    sold_cars = (
        db.query(SoldCars)
        .filter(SoldCars.dealer_id == dealer_id).all()
    )
    
    return [
        {
            "name": car.manufacturer_name,
            "model_name": car.model_name,
            "transmission": car.transmission,
            "year_produced": car.year_produced,
            "odometer_value": car.odometer_value,
            "price_usd": car.price_usd,
            "engine_type": car.engine_type,
            "body_type": car.body_type,
            "color": car.color,
            "previous_owners": car.previous_owners,
        }
        for car in sold_cars
    ]

@router.get("/recommendations", response_model=List[RecommendationBase])
async def get_recommendations(db: Session = Depends(get_db), dealer_id: Dealer = Depends(verify_token_from_cookie)):
    """
    Рекомендация машин для дилера из доступных, основываясь на его предыдущих продажах, 
    а также предсказание возможной цены, которую может выставить дилер для перепродажи.
    """
    # Получаем рекомендации для конкретного дилера
    recommendations = get_knn_recommendations(dealer_id, db)

    if recommendations is None or len(recommendations) == 0:
        # Если нет рекомендаций, возвращаем пустой список
        return []
    
    # Добавим отладку для проверки данных
    logging.info(f"Recommendations (before sorting): {recommendations.head()}")
    
    # Преобразуем типы данных, если необходимо, и удаляем NaN
    recommendations = recommendations.dropna()
    # recommendations = recommendations.sort_values(by=['distance'], ascending=True)
    recommendations = recommendations.head(20)

    # Преобразуем DataFrame в список словарей, чтобы вернуть его как JSON
    recommendations_dict = recommendations.to_dict(orient='records')

    # Проверка структуры данных перед возвратом
    logging.info(f"Recommendations (final): {recommendations_dict}")

    save_recommendations_to_db(recommendations_dict, dealer_id, db)

    return recommendations_dict

# @router.post("/add_dealer_car")
# def add_dealer_car(manufacturer_name: str, model_name: str, transmission: TransmissionEnum,
#                    year_produced: int, odometer_value: float, price_usd: float,
#                    engine_type: EngineTypeEnum, body_type: BodyTypeEnum, color: ColorEnum, previous_owners: PreviousOwnersEnum, db: Session = Depends(get_db),
#                    dealer_id: str = Depends(verify_token_from_cookie)):
#     """Добавление проданной дилером машины вручную."""
#     dealer_uuid = uuid.UUID(dealer_id)
#     car = SoldCars(dealer_id=dealer_uuid, manufacturer_name=manufacturer_name, model_name=model_name,
#                     transmission=transmission, year_produced=year_produced, odometer_value=odometer_value, 
#                     price_usd=price_usd, engine_type=engine_type, body_type=body_type, color=color,
#                     previous_owners=previous_owners)
#     db.add(car)
#     db.commit()
#     return {"message": "Sold car added successfully!"}
@router.post("/add_dealer_car")
def add_dealer_car(car: Car, db: Session = Depends(get_db), dealer_id: str = Depends(verify_token_from_cookie)):
    """Добавление проданной дилером машины вручную."""
    
    # Проверка пользователя через токен
    try:
        dealer_uuid = uuid.UUID(dealer_id)  # Преобразуем dealer_id в UUID
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid dealer ID")

    # Создание записи о машине
    new_car = SoldCars(
        dealer_id=dealer_uuid,
        manufacturer_name=car.manufacturer_name,
        model_name=car.model_name,
        transmission=car.transmission,
        year_produced=car.year_produced,
        odometer_value=car.odometer_value,
        price_usd=car.price_usd,
        engine_type=car.engine_type,
        body_type=car.body_type,
        color=car.color,
        previous_owners=car.previous_owners
    )

    # Добавление записи в базу данных
    db.add(new_car)
    db.commit()

    # Возвращаем сообщение об успешном добавлении
    return {"message": "Sold car added successfully!", "car": new_car}

@router.post("/upload_sales")
async def upload_sales(file: UploadFile = File(...), 
                       dealer_id: str = Depends(verify_token_from_cookie), 
                       db: Session = Depends(get_db)):
    """Загрузка CSV-файла и сохранение проданных автомобилей в БД для текущего дилера."""
    dealer_uuid = uuid.UUID(dealer_id)

    # Читаем CSV в DataFrame
    content = await file.read()
    # df = pd.read_csv(io.StringIO(content.decode('utf-8')), delimiter=detect_separator(io.StringIO(content.decode('utf-8'))), header=0)
    decoded_content = content.decode('utf-8')
    separator = detect_separator(decoded_content)  # Определяем разделитель
    df = pd.read_csv(io.StringIO(decoded_content), delimiter=separator, header=0)
    if df.empty:
        raise HTTPException(status_code=400, detail="Файл пуст или невалидный")

    df = preprocess_sold_data(df)

    # Загружаем в БД
    try:
        for _, row in df.iterrows():
            sold_car = SoldCars(
                dealer_id=dealer_uuid,
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
    except Exception as e:
        db.rollback()
        logging.error(f"Ошибка при загрузке данных: {str(e)}")
        raise HTTPException(status_code=500, detail="Ошибка сервера при обработке файла")

    return {"message": f"{len(df)} записей успешно загружены"}

from typing import List
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
import uuid
from datetime import datetime

@router.get("/dealers_previous_recommendations", response_model=List[dict])
def dealers_previous_recommendations(dealer_id: str = Depends(verify_token_from_cookie), db: Session = Depends(get_db)):
    """
    Получить информацию о рекомендованных автомобилях для дилера
    """
    dealer_id = uuid.UUID(dealer_id)
    
    # Query recommendations and join with CarsForSale to get car details, including predicted_price from Recommendations table
    previous_recommended_cars = (
        db.query(CarsForSale, Recommendations.predicted_price)  # Select car details and predicted_price from Recommendations
        .join(Recommendations, Recommendations.recommended_car_id == CarsForSale.id)
        .filter(Recommendations.dealer_id == dealer_id)
        .all()
    )
    
    # If no recommended cars found, raise 404 error
    if not previous_recommended_cars:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No recommended cars found for this dealer"
        )
    
    # Generate the list of recommended cars with predicted_price from Recommendations
    return [
        {
            "name": car.manufacturer_name,
            "model_name": car.model_name,
            "transmission": car.transmission,
            "year_produced": car.year_produced,
            "odometer_value": car.odometer_value,
            "price_usd": car.price_usd,
            "engine_type": car.engine_type,
            "body_type": car.body_type,
            "color": car.color,
            "previous_owners": car.previous_owners,
            "predicted_price": predicted_price,  # Fetch predicted_price from Recommendations table
        }
        for car, predicted_price in previous_recommended_cars
    ]
