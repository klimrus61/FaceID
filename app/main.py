from fastapi import FastAPI

app = FastAPI()

from app.core.config import settings


@app.get("/")
async def root():
    return {
        "message": "Hello World",
        "app_name": settings.app_name,
        "admin_email": settings.admin_email,
    }


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
