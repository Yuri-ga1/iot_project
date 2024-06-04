import uvicorn
from fastapi import Request

from .config import templates
from .config import app
from .config import logger

from .user_routs.router import router as user_router

app.include_router(user_router)

@app.get("/")
async def welcome(request: Request):
    return templates.TemplateResponse("welcome_page.html", {"request": request, "title": "Начальная страница"})

def start_server():
    """Launched with `poetry run start` at root level"""
    logger.info("Start server")
    uvicorn.run("server.main:app", host="127.0.0.1", port=8000, reload=False)
    