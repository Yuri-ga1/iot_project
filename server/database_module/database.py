from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime

from .tables import *

class Database:

    def __init__(self, db_name: str = "DATABASE"):
        self.db_name = db_name
        self.session = None

    async def connect(self):
        print("create connection")
        engine = create_engine(f'sqlite:///{self.db_name}.db')
        Base.metadata.create_all(engine)
        
        Session = sessionmaker(bind=engine)
        self.session = Session()
        
        
    async def disconnect(self):
        print("disconnect")
        self.session.close()


    async def add_device(self, mac: str, client_id: int):
        new_device = Device(
            MAC_address=mac,
            client_id=client_id
        )
        self.session.add(new_device)
        self.session.commit()
        
    async def add_client(self, name: str, phone: str):
        new_client = Client(
            name=name,
            phone_number=phone
        )
        self.session.add(new_client)
        self.session.commit()


    async def get_device_by_mac(self, mac: str):
        device = self.session.query(Device)\
            .filter(Device.MAC_address == mac)\
            .first()
        
        return device.id if device else None
        
        
    async def get_client_by_phone(self, phone: str):
        client = self.session.query(Client)\
            .filter(Client.phone_number == phone)\
            .first()
            
        return client.id if client else None
    
    async def save_data(
        self,
        device_id: int,
        smoke_level: float,
        gas_level: float,
        date: datetime
    ):
        new_data = Data(
            device_id=device_id,
            date=date,
            smoke_level=smoke_level,
            gas_level=gas_level
        )
        self.session.add(new_data)
        self.session.commit()
        

    async def get_data(self, device_id: int = None):
        if device_id:
            data = self.session.query(Data)\
                .filter(Data.device_id == device_id)\
                .all()
        else:
            data = self.session.query(Data).all()
            
        return data
        

database = Database()
