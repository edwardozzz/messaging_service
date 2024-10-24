from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str 
    password: str

class Message(BaseModel):
    sender_id: int
    recipient_id: int
    content: str
