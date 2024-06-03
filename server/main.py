import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request

from .config import database
from .config import templates

from .esp_routs.router import router as esp_router
from .user_routs.router import router as user_router

@asynccontextmanager
async def _lifespan(_app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()

app = FastAPI(lifespan=_lifespan)

app.include_router(esp_router)
app.include_router(user_router)

@app.get("/")
async def welcome(request: Request):
    return templates.TemplateResponse("welcome_page.html", {"request": request, "title": "Начальная страница"})

def start_server():
    """Launched with `poetry run start` at root level"""
    uvicorn.run("server.main:app", host="0.0.0.0", port=8000, reload=True)