from fastapi import FastAPI
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine



app = FastAPI() 
DATABASE_URL = "postgresql+psycopg2://postgres:password@localhost/ecommerce" 
engine = create_engine(DATABASE_URL)
sessionlocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()