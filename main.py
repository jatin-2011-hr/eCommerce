from fastapi import Depends,HTTPException
from Database.data import Base, engine, sessionlocal, app
from sqlalchemy.orm import Session
from AllModels.customer import Customer
from AllModels.manufacturer import Manufacturer
from AllModels.product import Product
from AllModels.order import Order
from AllSchema.schema import CustomerSchema,ManufacturerSchema,ProductSchema,CustomerResponse,ManufacturerResponse,ManufacturerLogin,CustomerLogin,OrderSchema,ChangePassword
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
@app.get("/customers", response_model=CustomerResponse)
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

# change customer password
@app.put("/customer/change-password/{customer_id}")
def change_customer_password(customer_id: int, data: ChangePassword, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()

    if not customer:
        raise HTTPException(status_code=404, detail="customer not found.")

    if not verify_password(data.old_password, customer.password):
        raise HTTPException(status_code=400, detail="old password is incorrect.")

    customer.password = hash_password(data.new_password)

    db.commit()
    db.refresh(customer)

    return {"detail": "Password updated successfully."}
# change manufacturer password
@app.put("/manufacturer/change-password/{manufacturer_id}") 
def change_manufacturer_password(manufacturer_id: int, data: ChangePassword, db: Session = Depends(get_db)):
    manufacturer = db.query(Manufacturer).filter(Manufacturer.manufacturer_id == manufacturer_id).first()
    if not manufacturer:
        raise HTTPException(status_code=404, detail="manufacturer not found.")
    
    if not verify_password(data.old_password, manufacturer.password):
        raise HTTPException(status_code=400, detail="old password is incorrect.")
    
    manufacturer.password = hash_password(data.new_password)
    db.commit()
    db.refresh(manufacturer)
    return {"detail": "Password updated successfully."}


# place order
@app.post("/order")
def create_order(order: OrderSchema, db: Session = Depends(get_db)):

    customer = db.query(Customer).filter(Customer.customer_id == order.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer does not exist")

    product = db.query(Product).filter(Product.product_id == order.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product does not exist")

    if product.stock < order.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    total_price = (product.MRP - product.Discount) * order.quantity

    product.stock -= order.quantity

    new_order = Order(
        customer_id=order.customer_id,
        product_id=order.product_id,
        quantity=order.quantity,
        total_price=total_price
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return {"detail": "Order created successfully","order_id": new_order.order_id}




# cancel order
@app.delete("/order/{order_id}")
def cancel_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.order_id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")

    db.delete(order)
    db.commit()
    return {"detail": "Order cancelled successfully."}

# delete customer
@app.delete("/customer/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found.")

    db.delete(customer)
    db.commit()

    return {"detail": "Customer deleted successfully."}

# delete manufacturer
@app.delete("/manufacturer/{manufacturer_id}")
def delete_manufacturer(manufacturer_id: int, db: Session = Depends(get_db)):
    manufacturer = db.query(Manufacturer).filter(Manufacturer.manufacturer_id == manufacturer_id).first()

    if not manufacturer:
        raise HTTPException(status_code=404, detail="Manufacturer not found.")

    db.delete(manufacturer)
    db.commit()

    return {"detail": "Manufacturer deleted successfully."}

# update customer
@app.put("/customer/update/{customer_id}")
def update_customer(customer_id: int, data: CustomerSchema, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found.")

    customer.name = data.name
    customer.email = data.email
    customer.phone_number = data.phone_number
    customer.address = data.address

    db.commit()
    db.refresh(customer)
    return {"detail": "Customer updated successfully.", "customer": customer}

# update manufacturer
@app.put("/manufacturer/update/{manufacturer_id}")
def update_manufacturer(manufacturer_id: int, data: ManufacturerSchema, db: Session = Depends(get_db)):
    manufacturer = db.query(Manufacturer).filter(Manufacturer.manufacturer_id == manufacturer_id).first()

    if not manufacturer:
        raise HTTPException(status_code=404, detail="Manufacturer not found.")

    manufacturer.name = data.name
    manufacturer.email = data.email
    manufacturer.phone_number = data.phone_number
    manufacturer.address = data.address

    db.commit()
    db.refresh(manufacturer)
    return {"detail": "Manufacturer updated successfully.", "manufacturer": manufacturer}


# update product
@app.put("/product/update/{product_id}")
def update_product(product_id: int, data: ProductSchema, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.product_id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    product.name = data.name
    product.description = data.description
    product.stock = data.stock
    product.MRP = data.MRP
    product.costPrice = data.costPrice
    product.Discount = data.Discount

    db.commit()
    db.refresh(product)
    return {"detail": "Product updated successfully.", "product": product}

# get product by id
@app.get("/product/{product_id}")
def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.product_id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    return product

# get all products
@app.get("/products")
def get_all_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return products