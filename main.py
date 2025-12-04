from fastapi import Depends,HTTPException
from Database.data import Base, engine, sessionlocal, app
from sqlalchemy.orm import Session
from AllModels.customer import Customer
from AllModels.manufacturer import Manufacturer
from AllModels.product import Product
from AllSchema.schema import CustomerSchema,ManufacturerSchema,ProductSchema,CustomerResponse,ManufacturerResponse,ManufacturerLogin,CustomerLogin
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2", "bcrypt"])

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


@app.on_event("startup")
def on_start(): 
    Base.metadata.create_all(bind=engine) 

def get_db():
     db: Session = sessionlocal()
     try:
        yield db 
     finally:
        db.close()


# add customer
@app.post("/customer", response_model=CustomerResponse)
def create_customer(customer: CustomerSchema, db: Session = Depends(get_db)):
    existing = db.query(Customer).filter(Customer.email == customer.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Customer with this email already exists.")

    new_customer = Customer(
        name=customer.name,
        email=customer.email,
        password=hash_password(customer.password),   
        phone_number=customer.phone_number,
        address=customer.address
    )

    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer    


# get all customers
@app.get("/customers", response_model=list[CustomerResponse])
def get_customers(db: Session = Depends(get_db)):
    customers = db.query(Customer).all()
    return customers


# get customer by id
@app.get("/customer/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found.")

    return customer  

# login customer
@app.post("/customer/get", response_model=CustomerResponse)
def get_customer_by_credentials(data: CustomerLogin, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.customer_id == data.customer_id).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found.")

    if not verify_password(data.password, customer.password):
        raise HTTPException(status_code=400, detail="Invalid password.")

    return customer   

                                                

# add manufacturer
@app.post("/manufacturer", response_model=ManufacturerResponse)
def create_manufacturer(manufacturer: ManufacturerSchema, db: Session = Depends(get_db)):
    existing = db.query(Manufacturer).filter(Manufacturer.email == manufacturer.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Manufacturer with this email already exists.") 

    new_manufacturer = Manufacturer(
        name=manufacturer.name,
        email=manufacturer.email,
        address=manufacturer.address,
        password=hash_password(manufacturer.password),   
        phone_number=manufacturer.phone_number
    )

    db.add(new_manufacturer)
    db.commit()
    db.refresh(new_manufacturer)
    return new_manufacturer      



# get all manufacturers
@app.get("/manufacturers", response_model=list[ManufacturerResponse])
def get_manufacturers(db: Session = Depends(get_db)):
    manufacturers = db.query(Manufacturer).all()
    return manufacturers


# get manufacturer by id
@app.get("/manufacturer/{manufacturer_id}", response_model=ManufacturerResponse)
def get_manufacturer(manufacturer_id: int, db: Session = Depends(get_db)):
    manufacturer = db.query(Manufacturer).filter(Manufacturer.manufacturer_id == manufacturer_id).first()

    if not manufacturer:
        raise HTTPException(status_code=404, detail="Manufacturer not found.")

    return manufacturer       

# login manufacturer
@app.post("/manufacturer/get", response_model=ManufacturerResponse)
def get_manufacturer_by_credentials(data: ManufacturerLogin, db: Session = Depends(get_db)):
    manufacturer = db.query(Manufacturer).filter(Manufacturer.manufacturer_id == data.manufacturer_id).first()

    if not manufacturer:
        raise HTTPException(status_code=404, detail="Manufacturer not found.")

    if not verify_password(data.password, manufacturer.password):
        raise HTTPException(status_code=400, detail="Invalid password.")

    return manufacturer 


# add product
@app.post("/product")
def create_product(product: ProductSchema, db: Session = Depends(get_db)):
    new_product = Product(
        name=product.name,
        description=product.description,
        stock=product.stock,
        MRP=product.MRP,
        costPrice=product.costPrice,
        Discount=product.Discount
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product