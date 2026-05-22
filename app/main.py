from fastapi import FastAPI

from app.database import Base, engine
from app.routers import auth, orders, products, users

Base.metadata.create_all(bind=engine)

app = FastAPI(title="E-Commerce API", version="1.0.0")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(orders.router)


@app.get("/health")
def health_check():
    return {"status": "healthy"}
