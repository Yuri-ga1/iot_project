import uvicorn
from fastapi import Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, Response
import hashlib

from .config import templates
from .config import app
from .config import logger
from .config import database
from .config import backend
from .config import cookie
from .config import SessionData
from uuid import uuid4

from .user_routs.router import router as user_router

app.include_router(user_router)


@app.get("/")
async def welcome(request: Request):
    return templates.TemplateResponse("welcome_page.html", {"request": request, "title": "Начальная страница"})

@app.get("/user_registration", response_class=HTMLResponse)
async def registration(request: Request):
    return templates.TemplateResponse("user_registration.html", {"request": request, "title": "Регистрация нового пользователя"})

@app.post("/user_registration_form_process")
async def registration(
    name: str = Form(...),
    login: str = Form(...),
    password: str = Form(...),
    email: str = Form(...)
):
    hashed_password = await hash_password(password)
    client_id = await database.get_client(login, hashed_password)
    
    if client_id is None:
        await database.add_client(
            name=name,
            login=login,
            password=hashed_password,
            email=email
        )
        
    return RedirectResponse(url="/", status_code=303)



@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "title": "Вход в аккаунт"})


@app.post("/auth/login")
async def login(
    response: Response,
    login: str = Form(...),
    password: str = Form(...),
):
    hashed_password = await hash_password(password)
    user_id = await database.get_client(login, hashed_password)
    
    session = uuid4()
    data = SessionData(
        username=login,
        user_pass=hashed_password
    )
    
    await backend.create(session, data)
    cookie.attach_to_response(response, session)
    return RedirectResponse(url="/user_panel", status_code=303, headers=response.headers)


def start_server():
    """Launched with `poetry run start` at root level"""
    logger.info("Start server")
    uvicorn.run("server.main:app", host="127.0.0.1", port=8000, reload=True)


async def hash_password(password: str) -> str:
    md5_hash = hashlib.md5()
    md5_hash.update(password.encode('utf-8'))
    return md5_hash.hexdigest()