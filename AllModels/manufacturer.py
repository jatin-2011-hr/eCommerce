from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from Database.data import Base

class Manufacturer(Base):
    __tablename__ = 'manufacturers'
    
    manufacturer_id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    email = Column(String, unique=True, nullable=False)
    address = Column(String, nullable=True)
    password = Column(String(100), nullable=False)
    phone_number = Column(String(30), nullable=True)