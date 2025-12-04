from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from Database.data import Base

class Product(Base):
    __tablename__ = 'products'
    
    product_id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(String, nullable=True)
    stock = Column(Integer, nullable=False)
    MRP = Column(Integer, nullable=False)
    costPrice = Column(Integer, nullable=False)
    Discount = Column(Integer, nullable=True)