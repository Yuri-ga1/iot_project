from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import hashlib

from ..config import templates
from ..config import database


router = APIRouter()


@router.get("/user_registration", response_class=HTMLResponse)
async def registration(request: Request):
    return templates.TemplateResponse("user_registration.html", {"request": request, "title": "Регистрация нового пользователя"})

@router.post("/user_registration_form_process")
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


@router.get("/device_registration", response_class=HTMLResponse)
async def registration(request: Request):
    return templates.TemplateResponse("device_registration.html", {"request": request, "title": "Регистрация нового девайса"})


@router.post("/device_registration_form_process")
async def device_registration(
    login: str = Form(...),
    password: str = Form(...),
    mac: str = Form(...)
):
    hashed_password = await hash_password(password)
    client_id = await database.get_client(login, hashed_password)
    if client_id is None:
        return RedirectResponse(url="user_registration", status_code=303)
    
    device_id = await database.get_device_by_mac(mac)
    
    if device_id is None:
        await database.add_device(
            mac=mac,
            client_id=client_id
        )
    return RedirectResponse(url="/", status_code=303)

async def hash_password(password: str) -> str:
    md5_hash = hashlib.md5()
    md5_hash.update(password.encode('utf-8'))
    return md5_hash.hexdigest()
    