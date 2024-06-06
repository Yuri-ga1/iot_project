import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ..config import logger

SMTP_SERVER = 'smtp.yandex.ru'
SMTP_PORT = 587  

EMAIL_ADDRESS = 'gas-smoke-detector@yandex.ru'
SENDER_EMAIL = EMAIL_ADDRESS 

def read_email_password(file_path):
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

path_email_pass = "emailPass.txt"
PASSWORD = read_email_password(path_email_pass)

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
    
async def send_message(recipient_email: str, notyce_type: int, **kwargs):
    """
    Parameters:
        recipient_email - Recipient's email
        notyce_type - Type of exceeded value: 0 - gas, 1 - smoke
        MAC_address - Device MAC address        
        room - device location
    """
    message = MIMEMultipart()
    message['From'] = SENDER_EMAIL
    message['To'] = recipient_email

    message['Subject'] = text_message[notyce_type]["Subject"]
    text = text_message[notyce_type]["text"].format(**kwargs)
    message.attach(MIMEText(text, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  
        server.login(EMAIL_ADDRESS, PASSWORD)
        text = message.as_string()
        server.sendmail(SENDER_EMAIL, recipient_email, text)
        logger.info("Notification sent successfully")
    except Exception as e:
        logger.error(f"An error occurred while sending the notice: {e}")
    finally:
        server.quit()