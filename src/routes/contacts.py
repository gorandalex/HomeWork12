from typing import List

from fastapi import Depends, HTTPException, APIRouter, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from ..database.db import get_db
from ..database.models import Contact, User
from ..schemas import ContactCreate, ContactResponse, ContactUpdate
from src.services.auth import auth_service

router = APIRouter(prefix='/contacts', tags=['/contact'])


@router.post("/", dependencies=[Depends(RateLimiter(times=1, seconds=10))], description='One request per 10 seconds')
def create_contact(contact: ContactCreate, db: Session = Depends(get_db), status_code=status.HTTP_201_CREATED,
                   _: User = Depends(auth_service.get_current_user)):
    db_contact = Contact(
        first_name=contact.first_name,
        last_name=contact.last_name,
        email=contact.email,
        phone=contact.phone_number,
        birthday=contact.birthday,
        notes=contact.notes,
    )
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


@router.get("/", response_model=List[ContactResponse], dependencies=[Depends(RateLimiter(times=1, seconds=10))],
            description='One request per 10 seconds')
def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                  _: User = Depends(auth_service.get_current_user)):
    contacts = db.query(Contact).offset(skip).limit(limit).all()
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse, dependencies=[Depends(RateLimiter(times=1, seconds=10))],
            description='One request per 10 seconds')
def read_contact(contact_id: int, db: Session = Depends(get_db),
                 _: User = Depends(auth_service.get_current_user)):
    db_contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact


@router.put("/{contact_id}", response_model=ContactResponse, dependencies=[Depends(RateLimiter(times=1, seconds=10))],
            description='One request per 10 seconds')
def update_contact(contact_id: int, contact: ContactUpdate, db: Session = Depends(get_db),
                   _: User = Depends(auth_service.get_current_user)):
    db_contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    for var, value in vars(contact).items():
        if value is not None:
            setattr(db_contact, var, value)
    db.commit()
    db.refresh(db_contact)
    return db_contact


@router.delete("/{contact_id}", dependencies=[Depends(RateLimiter(times=1, seconds=10))],
               description='One request per 10 seconds')
def delete_contact(contact_id: int, db: Session = Depends(get_db),
                   _: User = Depends(auth_service.get_current_user)):
    db_contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    db.delete(db_contact)
    db.commit()
    return {"message": "Contact deleted"}
