from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect  
from fastapi.middleware.cors import CORSMiddleware  
from sqlalchemy.orm import Session  
from sqlalchemy.future import select  
import jwt  
import json  
from datetime import datetime, timedelta  

# Импортируем необходимые модули вашего приложения  
from . import models, schemas, utils  
from .database import SessionLocal, engine  
from .crud import create_user  
from .models import Message  
from celery_worker import send_notification  # Импорт фоновый задачи для отправки уведомлений  
from fastapi.templating import Jinja2Templates  
from fastapi import Request  

# Инициализация FastAPI приложения  
app = FastAPI()  

# Добавляем поддержку CORS для разрешения запросов с указанных доменов  
origins = [  
    "http://localhost:8000",  
    "http://127.0.0.1:8000",  
]  

app.add_middleware(  
    CORSMiddleware,  
    allow_origins=["*"],  
    allow_credentials=True,  
    allow_methods=["*"],  
    allow_headers=["*"],  
)  

# Создание всех таблиц в базе данных при запуске приложения  
@app.on_event("startup")  
def startup():  
    models.Base.metadata.create_all(bind=engine)  

# Конфигурация JWT   
SECRET_KEY = "349b6f9e307a2d4504828cf5c5a5be25c9cd1de1a9cebcd88815305e9d0672d6"  
ALGORITHM = "HS256"  
ACCESS_TOKEN_EXPIRE_MINUTES = 30  

# Генерация JWT токена  
def create_access_token(data: dict, expires_delta: timedelta = None):  
    to_encode = data.copy()  
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))  
    to_encode.update({"exp": expire})  
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  

# Функция для получения сессии базы данных  
def get_db():  
    db = SessionLocal()  
    try:  
        yield db  
    finally:  
        db.close()  

# Хранение подключенных клиентов WebSocket  
connected_clients = {}  

@app.websocket("/ws/{user_id}")  
async def websocket_endpoint(websocket: WebSocket, user_id: str):  
    """WebSocket эндпоинт для обмена сообщениями."""  
    await websocket.accept()  
    connected_clients[user_id] = websocket  

    try:  
        while True:  
            # Получаем данные от клиента  
            data = await websocket.receive_text()  
            message_data = json.loads(data)  # Декодируем JSON данные  
            recipient_id = message_data.get("recipientId")  
            message_content = message_data.get("content")  

            # Сохраняем сообщение в базе данных  
            with SessionLocal() as db:  
                save_message(db, sender_id=user_id, recipient_id=recipient_id, content=message_content)  

            # Отправляем сообщение выбранному получателю, если он подключен  
            if recipient_id in connected_clients:  
                await connected_clients[recipient_id].send_text(  
                    json.dumps({"sender": user_id, "content": message_content})  
                )  
            else:  
                # Если получатель не подключен, отправляем уведомление через Telegram-бота  
                send_notification.delay(recipient_id, message_content)  

    except WebSocketDisconnect:  
        del connected_clients[user_id]  # Удаляем клиента из списка подключенных  

def save_message(db: Session, sender_id: int, recipient_id: int, content: str):  
    """Сохранение сообщения в базе данных."""  
    message = Message(content=content, sender_id=sender_id, recipient_id=recipient_id)  
    db.add(message)  
    db.commit()  
    db.refresh(message)  

# Эндпоинт для регистрации пользователей  
@app.post("/register/")  
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):  
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()  
    if existing_user:  
        raise HTTPException(status_code=400, detail="Email already registered")  
    return create_user(db=db, user=user)  

# Эндпоинт для входа пользователей  
@app.post("/login/")  
async def login(user: schemas.UserLogin, db: Session = Depends(get_db)):  
    stmt = select(models.User).where(models.User.email == user.email)  

    result = db.execute(stmt)  
    db_user = result.scalars().first()  
    
    if not db_user or not utils.verify_password(user.password, db_user.hashed_password):  
        raise HTTPException(status_code=400, detail="Invalid credentials")  

    access_token = create_access_token(data={"sub": db_user.email})  
    return {"access_token": access_token, "user_id": db_user.id}  

# Настройка Jinja2 для работы с шаблонами  
templates = Jinja2Templates(directory="app/templates")  

# Эндпоинт для отображения страницы чата  
@app.get("/chat/")  
async def chat(request: Request):  
    return templates.TemplateResponse("chat.html", {"request": request})  

# Эндпоинт для получения списка пользователей  
@app.get("/users/")  
async def get_users(db: Session = Depends(get_db)):  
    users = db.query(models.User).all()  
    return [{"id": user.id, "email": user.email} for user in users]  

def get_message_history(db: Session, sender_id: int, recipient_id: int):  
    """Получение истории сообщений между двумя пользователями."""  
    return db.query(Message).filter(  
        ((Message.sender_id == sender_id) & (Message.recipient_id == recipient_id)) |  
        ((Message.sender_id == recipient_id) & (Message.recipient_id == sender_id))  
    ).all()  

# Эндпоинт для получения истории сообщений между двумя пользователями  
@app.get("/messages/history/{user_id_1}/{user_id_2}")  
async def message_history(user_id_1: int, user_id_2: int, db: Session = Depends(get_db)):  
    history = get_message_history(db, sender_id=user_id_1, recipient_id=user_id_2)  
    return [{"sender_id": msg.sender_id, "recipient_id": msg.recipient_id, "content": msg.content} for msg in history]