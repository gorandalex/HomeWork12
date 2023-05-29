from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    birthday: Optional[date] = None
    notes: Optional[str] = None


class ContactCreate(ContactBase):
    pass


class ContactUpdate(ContactBase):
    id: int


class Contact(ContactBase):
    id: int

    class Config:
        orm_mode = True


class ContactList(BaseModel):
    contacts: List[Contact]
    total: int


class ContactFilter(BaseModel):
    search: Optional[str] = None
    skip: int = 0
    limit: int = 100


class ContactResponse(ContactBase):
    id: int

    class Config:
        orm_mode = True

class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=16)
    email: str
    password: str = Field(min_length=6, max_length=10)


class UserDb(BaseModel):
    id: int
    username: str
    email: str
    avatar: str

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    

class RequestEmail(BaseModel):
    email: EmailStr