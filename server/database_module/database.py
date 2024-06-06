from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, desc, extract
from datetime import datetime, date

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


    async def add_device(self, mac: str, room: str, client_id: int):
        new_device = Device(
            MAC_address=mac,
            room=room,
            client_id=client_id
        )
        self.session.add(new_device)
        self.session.commit()
        
    async def add_client(self, name: str, login: str, password: str, email: str):
        new_client = Client(
            name=name,
            login=login,
            password=password,
            email=email
        )
        self.session.add(new_client)
        self.session.commit()

    async def add_notice(self, device_id: int, notice_type: bool, date: datetime):
        new_notice = Notice(
            device_id=device_id,
            notice_type=notice_type,
            date=date
        )
        self.session.add(new_notice)
        self.session.commit()

    async def get_client_id_by_mac(self, mac: str):
        device = self.session.query(Device)\
            .filter(Device.MAC_address == mac)\
            .first()
        return device.client_id if device else None
    
    async def get_macs_by_id_client(self, client_id: int):
        device = self.session.query(Device)\
            .filter(Device.client_id == client_id)\
            .all()
        macs = [device.MAC_address for device in device if device.MAC_address]
        return macs if len(macs) != 0 else None
    
    async def get_room_by_mac(self, mac: str):
        device = self.session.query(Device)\
            .filter(Device.MAC_address == mac)\
            .first()
        return device.room if device else None
    
    async def get_email_by_id(self, id: int):
        client = self.session.query(Client)\
            .filter(Client.id == id)\
            .first()
        return client.email if client else None

    async def get_date_notice_by_device_id_type(self, device_id: int, notice_type: bool):
        notice = self.session.query(Notice)\
            .filter(Notice.device_id == device_id, Notice.notice_type == notice_type)\
            .order_by(desc(Notice.date))\
            .first()
        return notice.date if notice else None


    async def get_device_by_mac(self, mac: str):
        device = self.session.query(Device)\
            .filter(Device.MAC_address == mac)\
            .first()
        
        return device.id if device else None
    
    def get_id_device_by_mac(self, mac: str):
        device = self.session.query(Device)\
            .filter(Device.MAC_address == mac)\
            .first()
        
        return device.id if device else None
    
    async def get_devices_mac(self):
        macs = self.session.query(Device.MAC_address).all()
        
        return macs if macs else None
        
        
    async def get_client(self, login: str, hashed_password: str):
        client = self.session.query(Client)\
            .filter(Client.login == login, Client.password == hashed_password)\
            .first()
            
        return client.id if client else None
    
    async def get_client_by_id(self, user_id: int):
        id = self.session.query(Client)\
            .filter(Client.id == user_id)\
            .first()
            
        return id if id else None
    
    async def check_data_availability_by_date(self, device_id: int, date: datetime):
        data = self.session.query(Data)\
        .filter(Data.device_id == device_id, Data.date == date)\
        .first()
        return True if data else False
    
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
    
    def get_data_by_date(self, device_id: int, date: datetime):
        data = self.session.query(Data)\
            .filter(
                Data.device_id == device_id,
                extract('year', Data.date) == date.year,
                extract('month', Data.date) == date.month,
                extract('day', Data.date) == date.day
            )\
            .all()
            
        return data