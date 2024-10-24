from celery import Celery
from aiogram import Bot
from app.database import SessionLocal
from app.models import User
import logging

# Инициализация бота
API_TOKEN = '7981185062:AAG6sxlPQPMN5OU1g1uh3LGTazP_Latv2zo'
bot = Bot(token=API_TOKEN)

# Инициализация Celery
celery_app = Celery('messaging_service', broker='redis://localhost:6379/0')

# Обновление конфигурации Celery
celery_app.conf.update(
    task_routes={'*': {'queue': 'default'}},
    worker_pool='threads',  # Использование потоков вместо процессов
)

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Фоновая задача отправки уведомления
@celery_app.task
async def send_notification(user_telegram_id: int, message: str):
    try:
        await bot.send_message(user_telegram_id, message)
        logging.info(f"Уведомление успешно отправлено пользователю {user_telegram_id}: {message}")
    except Exception as e:
        logging.error(f"Ошибка при отправке уведомления пользователю {user_telegram_id}: {e}")

# Функция для отправки уведомления
def notify_user(user_telegram_id: int, message: str):
    send_notification.delay(user_telegram_id, message)

def get_telegram_id(user_id: str) -> int:
    with SessionLocal() as db:
        user = db.query(User).filter(User.id == user_id).first()  # Предполагаем, что у вас есть модель User
        return user.telegram_id if user else None
