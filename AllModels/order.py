from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from Database.data import Base
from AllModels.customer import Customer

class Order(Base):
    __tablename__ = 'orders'
    
    order_id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.customer_id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    total_price = Column(Integer, nullable=False)
    
    customer = relationship("Customer", back_populates="orders")
    product = relationship("Product", back_populates="orders")