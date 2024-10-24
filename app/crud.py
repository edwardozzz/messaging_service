from sqlalchemy.orm import Session  # Импортируем класс Session из SQLAlchemy для работы с базой данных  
from .models import User  # Импортируем модель User, которая определяет структуру таблицы пользователей  
from .schemas import UserCreate  # Импортируем схему UserCreate, используемую для валидации данных при создании пользователя  
from .utils import hash_password  # Импортируем функцию для хеширования паролей  

# Функция для создания нового пользователя в базе данных  
def create_user(db: Session, user: UserCreate):  
    # Хешируем введённый пароль пользователя для безопасности  
    hashed_password = hash_password(user.password)  
    
    # Создаём экземпляр модели User с заданными данными (электронная почта, хешированный пароль, имя пользователя)  
    db_user = User(email=user.email, hashed_password=hashed_password, username=user.username)  
    
    # Добавляем нового пользователя в сеанс базы данных  
    db.add(db_user)  
    
    # Фиксируем изменения в базе данных (сохраняем нового пользователя)  
    db.commit()  
    
    # Обновляем объект db_user, чтобы отобразить все изменения и получить дополнительные поля из базы данных (например, сгенерированное ID)  
    db.refresh(db_user)  
    
    # Возвращаем созданного пользователя, чтобы использовать его в дальнейшем  
    return db_user