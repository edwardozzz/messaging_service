from sqlalchemy import create_engine  # Импортируем функцию create_engine для создания подключения к базе данных  
from sqlalchemy.ext.declarative import declarative_base  # Импортируем declarative_base для создания базового класса моделей  
from sqlalchemy.orm import sessionmaker  # Импортируем sessionmaker для создания новых сеансов работы с базой данных  

# Задаем URL для подключения к PostgreSQL  
# Формат: 'postgresql://<username>:<password>@<host>:<port>/<database>'  
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:123@db:5432/messaging_service"  

# Создаем объект engine, который управляет подключением к базе данных по указанному URL  
engine = create_engine(SQLALCHEMY_DATABASE_URL)  

# Создаем фабрику сеансов, настраивая параметры (отключение автокоммита и автозаписи)  
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  

# Создаем базовый класс для моделей, который будет использоваться для декларативного стиля определения моделей SQLAlchemy  
Base = declarative_base()  

# Создаем зависимость для использования сессии базы данных в маршрутах FastAPI  
def get_db():  
    # Создаем новый экземпляр сессии работы с базой данных  
    db = SessionLocal()  
    try:  
        yield db  # Возвращаем созданную сессию, чтобы ее можно было использовать в маршруте  
    finally:  
        db.close()  # Закрываем сессию после ее использования, чтобы освободить ресурсы