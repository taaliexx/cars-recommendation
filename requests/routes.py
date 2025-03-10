from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from database import get_db
from models import Dealer, CarsForSale, SoldCars
from typing import List
from recommendations import get_knn_recommendations, save_recommendations_to_db
from schemas import RecommendationBase
import uuid
import logging 
from utils import verify_token_from_cookie

router = APIRouter(prefix="", tags=["requests"])

@router.get("/cars_for_sale", response_model=List[dict])
def get_cars(db: Session = Depends(get_db)):
    """
    Cписок всех машин, которые можно приобрести для дальнейшей продажи.
    """
    cars_for_sale = db.query(CarsForSale).limit(10).all()
    return [{"id": str(car.id), 
             "manufacturer name": car.manufacturer_name, 
             "model": car.model_name} for car in cars_for_sale]

@router.get("/dealers_cars", response_model=List[dict])
def get_dealers_cars(dealer_id: str = Depends(verify_token_from_cookie), db: Session = Depends(get_db)):
    """
    Cписок машин, проданных конкретным дилером.
    """
    dealer_id = uuid.UUID(dealer_id)
    sold_cars = (
        db.query(SoldCars)
        .filter(SoldCars.dealer_id == dealer_id).all()
    )
    
    return [
        {
            "id": str(car.id),
            "manufacturer_name": car.manufacturer_name,
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
    recommendations = recommendations.head(10)

    # Преобразуем DataFrame в список словарей, чтобы вернуть его как JSON
    recommendations_dict = recommendations.to_dict(orient='records')

    # Проверка структуры данных перед возвратом
    logging.info(f"Recommendations (final): {recommendations_dict}")

    save_recommendations_to_db(recommendations_dict, dealer_id, db)

    return recommendations_dict