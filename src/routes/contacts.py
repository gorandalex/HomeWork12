from typing import List

from fastapi import Depends, HTTPException, APIRouter, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from ..database.db import get_db
from ..database.models import Contact, User
from ..schemas import ContactCreate, ContactResponse, ContactUpdate
from src.services.auth import auth_service
from src.repository import contacts as repository_contacts

router = APIRouter(prefix='/contacts', tags=['/contact'])


@router.post("/", dependencies=[Depends(RateLimiter(times=1, seconds=10))], description='One request per 10 seconds')
async def create_contact(contact: ContactCreate, db: Session = Depends(get_db), status_code=status.HTTP_201_CREATED,
                         current_user: User = Depends(auth_service.get_current_user)):
    contact_email = await repository_contacts.search_contact(owner_id=current_user.id, email=contact.email, db=db)
    if contact_email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Email is exists')
    contact = await repository_contacts.create_contact(owner_id=current_user.id, body=contact, db=db)
    return contact


@router.get("/", response_model=List[ContactResponse], dependencies=[Depends(RateLimiter(times=1, seconds=10))],
            description='One request per 10 seconds')
def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                  current_user: User = Depends(auth_service.get_current_user)):
    contacts = db.query(Contact).offset(skip).limit(limit).all()
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse, dependencies=[Depends(RateLimiter(times=1, seconds=10))],
            description='One request per 10 seconds')
def read_contact(contact_id: int, db: Session = Depends(get_db),
                 current_user: User = Depends(auth_service.get_current_user)):
    db_contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found!")
    return db_contact


@router.put("/{contact_id}", response_model=ContactResponse, dependencies=[Depends(RateLimiter(times=1, seconds=10))],
            description='One request per 10 seconds')
def update_contact(contact_id: int, contact: ContactUpdate, db: Session = Depends(get_db),
                   current_user: User = Depends(auth_service.get_current_user)):
    db_contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found!")
    for var, value in vars(contact).items():
        if value is not None:
            setattr(db_contact, var, value)
    db.commit()
    db.refresh(db_contact)
    return db_contact


@router.delete("/{contact_id}", dependencies=[Depends(RateLimiter(times=1, seconds=10))],
               description='One request per 10 seconds')
def delete_contact(contact_id: int, db: Session = Depends(get_db),
                   current_user: User = Depends(auth_service.get_current_user)):
    db_contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found!")
    db.delete(db_contact)
    db.commit()
    return {"message": "Contact deleted"}


@router.get('/birthdays/{days}', response_model=List[ContactResponse],
            dependencies=[Depends(RateLimiter(times=1, seconds=1))])
async def upcoming_birthdays_list(days: int, db: Session = Depends(get_db),
                                  current_user: User = Depends(auth_service.get_current_user)):
    birthdays = await repository_contacts.search_birthday_contact(owner_id=current_user.id, db=db, days=days)
    if len(birthdays) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'There are no birthdays')
    return birthdays
