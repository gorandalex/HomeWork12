from datetime import date, timedelta
from typing import List, Optional

from sqlalchemy import and_, or_, func, text
from sqlalchemy.orm import Session

from src.database.models import Contact
from src.schemas import ContactBase as ContactModel


async def get_contacts(db: Session, owner_id: int) -> List[Contact]:
    contacts = db.query(Contact).filter_by(owner_id=owner_id).all()
    return contacts


async def get_contact(contact_id: int, db: Session, owner_id: int) -> Contact:
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.owner_id == owner_id)).first()
    return contact


async def create_contact(body: ContactModel, db: Session, owner_id: int) -> Contact:
    contact = Contact(**body.dict())
    contact.owner_id = owner_id
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact(body: ContactModel, contact_id: int, db: Session, owner_id: int) -> Contact:
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.owner_id == owner_id)).first()
    if contact:
        contact.email = body.email
        contact.phone = body.phone
        contact.birthday = body.birthday
        contact.notes = body.notes
        db.commit()
    return contact


async def delete_contact(contact_id: int, db: Session, owner_id: int) -> Contact:
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.owner_id == owner_id)).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def search_contact(
        db: Session,
        owner_id: int,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
) -> List[Contact]:
    contact = db.query(Contact).filter(
        and_(
            or_(Contact.first_name == first_name, first_name is None),
            or_(Contact.last_name == last_name, last_name is None),
            or_(Contact.email == email, email is None),
            Contact.owner_id == owner_id,
        )
    ).all()

    return contact


async def search_birthday_contact(db: Session, owner_id: int, days: int = 7) -> List[Contact]:
    date_from = date.today()
    date_to = date.today() + timedelta(days=days)
    this_year = date_from.year
    next_year = date_from.year + 1
    contact = db.query(Contact).filter(
        and_(
            Contact.owner_id == owner_id,
        )).filter(
        or_(
            func.to_date(func.concat(func.to_char(Contact.birthday, "DDMM"), this_year), "DDMMYYYY").between(date_from,
                                                                                                             date_to),
            func.to_date(func.concat(func.to_char(Contact.birthday, "DDMM"), next_year), "DDMMYYYY").between(date_from,
                                                                                                             date_to),
        )
    ).all()

    return contact
