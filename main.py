from fastapi import FastAPI
from routers import users
from routers import companies
from routers import subscriptions
from routers import payments
from routers import conversions
import uvicorn
app = FastAPI(title="Main API")
app.include_router(users.router)
app.include_router(companies.router)
app.include_router(subscriptions.router)
app.include_router(payments.router)
app.include_router(conversions.router)


@app.get("/")
def home():
    return {"message":"Welcome to the API"}


if __name__ == "__main__":
    uvicorn.run("main:app",reload=True)