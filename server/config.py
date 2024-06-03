from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="server/templates")

from .database_module.database import Database

database = Database()