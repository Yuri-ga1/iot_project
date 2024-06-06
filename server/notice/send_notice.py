import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import os

from ..config import logger
from ..config import database

SMTP_SERVER = 'smtp.yandex.ru'
SMTP_PORT = 587  

EMAIL_ADDRESS = 'gas-smoke-detector@yandex.ru'
SENDER_EMAIL = EMAIL_ADDRESS 

NAME_PASS = "emailPass.txt"

def read_email_password(file_name):
    current_file_path = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file_path)
    file_path = os.path.join(current_dir, file_name)
    try:
        with open(file_path, 'r') as file:
            api_key = file.readline().strip()
        return api_key
    except FileNotFoundError:
        logger.error(f"File {file_path} was not found.")
        return None
    except Exception as e:
        logger.error(f"Error reading password: {e}")
        return None

text_message = {
    0: {
        "Subject": "Превышение газа",
        "text": "Детектор газа и дыма {MAC_address} расположенный в {room} превысил допустимое значение газа! Проверьте обстановку!"
    },
    1: {
        "Subject": "Превышение дыма",
        "text": "Детектор газа и дыма {MAC_address} расположенный в {room} превысил допустимое значение дыма! Проверьте обстановку!"
    }
}
    
def send_message(recipient_email: str, notice_type: int, **kwargs):
    """
    Parameters:
        recipient_email - Recipient's email
        notyce_type - Type of exceeded value: 0 - gas, 1 - smoke
        MAC_address - Device MAC address        
        room - device location
    """
    password = read_email_password(NAME_PASS)
    message = MIMEMultipart()
    message['From'] = SENDER_EMAIL
    message['To'] = recipient_email

    message['Subject'] = text_message[notice_type]["Subject"]
    text = text_message[notice_type]["text"].format(**kwargs)
    message.attach(MIMEText(text, 'plain'))
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  
        server.login(EMAIL_ADDRESS, password)
        text = message.as_string()
        server.sendmail(SENDER_EMAIL, recipient_email, text)
        logger.info("Notification sent successfully")
    except Exception as e:
        logger.error(f"An error occurred while sending the notice: {e}")
    finally:
        server.quit()

async def checking_elapsed_time(notice_type: int, device_id: int, current_datetime: datetime):
    date_last_notice = await database.get_date_notice_by_device_id_type(device_id, bool(notice_type))
    if date_last_notice is None:
        return True
    time_difference = current_datetime - date_last_notice

    ten_minutes = timedelta(minutes=10)
    if time_difference >= ten_minutes:
        return True
    else:
        return False
    
async def send_email(mac_address, device_id, current_datetime, notice_type):
    id_client = await database.get_client_id_by_mac(mac_address)
    recipient_email = await database.get_email_by_id(id_client)
    room = await database.get_room_by_mac(mac_address)
    if await checking_elapsed_time(notice_type, device_id, current_datetime):
        send_message(recipient_email, notice_type, MAC_address=mac_address, room=room)
        await database.add_notice(device_id, bool(notice_type), current_datetime)