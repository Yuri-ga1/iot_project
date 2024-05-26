import uvicorn
from fastapi import FastAPI

from .database_module.database import database
from .esp_routs.router import router as esp_router

app = FastAPI()

app.include_router(esp_router)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/")
async def welcome():
    return {"message": "Hello World"}

def start_server():
    """Launched with `poetry run start` at root level"""
    uvicorn.run("server.main:app", host="0.0.0.0", port=8000, reload=True)