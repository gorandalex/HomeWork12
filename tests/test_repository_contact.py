import datetime
import unittest
from unittest.mock import MagicMock
from datetime import date

from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import Contact as ContactModel
from src.repository.contacts import (
    get_contacts,
    search_contact,
    get_contact,
    create_contact,
    update_contact,
    delete_contact,
    search_birthday_contact,
)


class TestContacts(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)
        self.contact_test = Contact(
            id=1,
            first_name='user1',
            last_name='last_name',
            email='user1@example.com',
            phone='0631111111',
            birthday=datetime.date(year=1978, month=9, day=9),
            notes='Notes',
            owner_id=1,
        )

    async def test_get_contacts(self):
        user = self.user
        session = self.session

        expected_contacts = [
            Contact(id=1, owner_id=1, first_name='Test1', last_name='Test1', email='test1@example.com',
                    birthday=date.today()),
            Contact(id=2, owner_id=1, first_name='Test2', last_name='Test2', email='test2@example.com',
                    birthday=date.today())
        ]

        session.query(Contact).filter_by(owner_id=user.id).all.return_value = expected_contacts

        contacts = await get_contacts(owner_id=user.id, db=session)

        self.assertEqual(contacts, expected_contacts)

    async def test_get_contact(self):
        user = self.user
        session = self.session
        expected_contact = self.contact_test

        session.query(Contact).filter(and_(Contact.id == expected_contact.id, Contact.owner_id == user.id)).first. \
            return_value = expected_contact

        contact = await get_contact(contact_id=expected_contact.id, owner_id=expected_contact.owner_id, db=session)

        self.assertEqual(contact, expected_contact)

    async def test_create_contact(self):
        user = self.user
        expected_contact = self.contact_test
        session = self.session

        add_mock = session.add
        commit_mock = session.commit

        contact = await create_contact(body=ContactModel(**expected_contact.__dict__),
                                       db=self.session,
                                       owner_id=user.id)

        self.assertEqual(contact.first_name, expected_contact.first_name)
        self.assertEqual(contact.last_name, expected_contact.last_name)
        self.assertEqual(contact.email, expected_contact.email)
        self.assertEqual(contact.phone, expected_contact.phone)
        self.assertEqual(str(contact.birthday), str(expected_contact.birthday))
        self.assertEqual(contact.notes, expected_contact.notes)
        add_mock.assert_called_once_with(contact)
        commit_mock.assert_called_once()

    async def test_update_contact(self):
        user = self.user
        expected_contact = self.contact_test
        session = self.session

        session.query(Contact).filter(and_(Contact.id == expected_contact.id, Contact.owner_id == user.id)).first \
            .return_value = expected_contact

        commit_mock = session.commit

        contact = await update_contact(body=ContactModel(**expected_contact.__dict__),
                                       contact_id=expected_contact.id,
                                       db=session,
                                       owner_id=user.id)

        self.assertEqual(contact, self.contact_test)
        self.assertEqual(contact.first_name, expected_contact.first_name)
        self.assertEqual(contact.last_name, expected_contact.last_name)
        self.assertEqual(contact.email, expected_contact.email)
        self.assertEqual(contact.phone, expected_contact.phone)
        self.assertEqual(contact.birthday, expected_contact.birthday)
        self.assertEqual(contact.notes, expected_contact.notes)
        commit_mock.assert_called_once()

    async def test_delete_contact(self):
        user = self.user
        expected_contact = self.contact_test
        session = self.session

        query_mock = self.session.query.return_value
        filter_mock = query_mock.filter.return_value
        filter_mock.first.return_value = self.contact_test

        delete_mock = self.session.delete
        commit_mock = self.session.commit

        contact = await delete_contact(contact_id=expected_contact.id,
                                       db=session,
                                       owner_id=user.id)

        self.assertEqual(contact, self.contact_test)
        delete_mock.assert_called_once_with(contact)
        commit_mock.assert_called_once()

    async def test_search_contact(self):
        user = self.user
        expected_contact = self.contact_test
        session = self.session

        first_name = 'test'
        last_name = None
        email = None

        session.query(Contact).filter(
            and_(
                or_(Contact.first_name == first_name, first_name is None),
                or_(Contact.last_name == last_name, last_name is None),
                or_(Contact.email == email, email is None),
                Contact.owner_id == user.id,
            )
        ).all.return_value = [expected_contact]

        contacts = await search_contact(owner_id=user.id,
                                        first_name=first_name,
                                        last_name=last_name,
                                        email=email,
                                        db=self.session)

        self.assertEqual(contacts, [self.contact_test])

    async def test_search_birthday_contact(self):
        user = self.user
        session = self.session

        date_from = date.today()
        date_to = date.today() + datetime.timedelta(days=7)
        this_year = date_from.year
        next_year = date_from.year + 1
        today = date.today()
        contacts = [
            Contact(id=1, first_name='John', last_name='Doe', email='john@example.com', birthday=today),
            Contact(id=2, first_name='Jane', last_name='Smith', email='jane@example.com', birthday=today),
        ]
        session.query(Contact).filter(
            and_(
                Contact.owner_id == user.id,
            )).filter(
            or_(
                func.to_date(func.concat(func.to_char(Contact.birthday, "DDMM"), this_year), "DDMMYYYY").between(
                    date_from,
                    date_to),
                func.to_date(func.concat(func.to_char(Contact.birthday, "DDMM"), next_year), "DDMMYYYY").between(
                    date_from,
                    date_to),
            )
        ).all.return_value = contacts

        result = await search_birthday_contact(owner_id=user.id, db=session)

        self.assertEqual(len(result), len(contacts))

        for i in range(len(result)):
            self.assertEqual(result[i].id, contacts[i].id)
            self.assertEqual(result[i].first_name, contacts[i].first_name)
            self.assertEqual(result[i].last_name, contacts[i].last_name)
            self.assertEqual(result[i].email, contacts[i].email)
            self.assertEqual(result[i].birthday, contacts[i].birthday)


if __name__ == '__main__':
    unittest.main()