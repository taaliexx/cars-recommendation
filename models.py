from sqlalchemy import Column, String, UUID, TIMESTAMP, func, Integer, ForeignKey, Numeric, TIMESTAMP, Float
from sqlalchemy.orm import relationship
from database import Base
import uuid

class Dealer(Base):
    __tablename__ = "dealers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, default=func.now())

    sold_cars = relationship("SoldCars", back_populates="dealer", cascade="all, delete-orphan")


class CarsForSale(Base):
    __tablename__ = "cars_for_sale"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    manufacturer_name = Column(String, nullable=False)
    model_name = Column(String, nullable=False)
    transmission = Column(String, nullable=False)
    year_produced = Column(Integer, nullable=False)
    odometer_value = Column(String, nullable=False)
    price_usd = Column(Numeric, nullable=False)
    engine_type = Column(String, nullable=False)
    body_type = Column(String, nullable=False)
    color = Column(String, nullable=False)
    previous_owners = Column(String, nullable=False)

class SoldCars(Base):
    __tablename__ = "saled_cars"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dealer_id = Column(String, ForeignKey("dealers.id", ondelete="CASCADE"))
    manufacturer_name = Column(String, nullable=False)
    model_name = Column(String, nullable=False)
    transmission = Column(String, nullable=False)
    year_produced = Column(Integer, nullable=False)
    odometer_value = Column(String, nullable=False)
    price_usd = Column(Numeric, nullable=False)
    engine_type = Column(String, nullable=False)
    body_type = Column(String, nullable=False)
    color = Column(String, nullable=False)
    previous_owners = Column(String, nullable=False)

    dealer = relationship("Dealer", back_populates="sold_cars")

class Recommendations(Base):
    __tablename__ = "recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dealer_id = Column(UUID(as_uuid=True), ForeignKey("dealers.id", ondelete="CASCADE"))
    recommended_car_id = Column(UUID(as_uuid=True), ForeignKey("cars_for_sale.id", ondelete="CASCADE"))
    distance = Column(Numeric, nullable=False)
    predicted_price = Column(Numeric, nullable=False)
    profit = Column(Numeric, nullable=False)
    created_at = Column(String, default="NOW()")