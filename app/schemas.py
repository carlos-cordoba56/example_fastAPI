from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from pydantic import EmailStr
from pydantic.types import conint


class PostBase(BaseModel):
    ''' Esta clase define el formato de la petición (Request) que realiza el usuario'''

    title: str
    content: str
    published: bool = True

class PostCreate(PostBase):
    pass

class PostUpdate(PostBase):
    pass

class UserResponce(BaseModel):
    # id: int
    email: EmailStr
    # password: str
    created_at: datetime

    class Config:
        orm_mode = True

class PostRespoce(BaseModel):
    ''' Esta clase define el formato de la respuesta (Responce) hacia el usuario'''

    # id: int
    title: str
    content: str
    published: bool
    created_at: datetime
    # owner_id: int
    owner: UserResponce

    class Config:
        orm_mode = True

class PostRespoceWithVotes(BaseModel):
    ''' Esta clase define el formato de la respuesta (Responce) hacia el usuario'''

    Post: PostRespoce
    votes: int

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str



class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token = str
    token_type = str

    class Config:
        orm_mode = True

class TokenData(BaseModel):
    id: Optional[str] = None

class Vote(BaseModel):
    post_id: int
    dir: conint(le=1)