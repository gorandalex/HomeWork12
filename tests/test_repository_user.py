import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel, UserDb
from src.repository.users import (
    get_user_by_email,
    create_user,
    confirmed_email,
    update_token
    )


class TestUsers(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = MagicMock(spec=User)
        self.user_test = User(
            id=1,
            username='username',
            password='password',
            email='user1@example.com',
            confirmed='False',
            avatar='https://example.com/avatar.jpg'
        )

    async def test_get_user_by_email(self):
        db_mock = self.session

        # Create some dummy user data
        user1 = User(email='user1@example.com')
        user2 = User(email='user2@example.com')
        user3 = User(email='user3@example.com')

        self.session.query().filter().first.return_value = user1
        result = await get_user_by_email('user1@example.com', db_mock)
        self.assertEqual(result, user1)

        # Test case 2: User does not exist in the database
        self.session.query().filter().first.return_value = None
        result = await get_user_by_email('user4@example.com', db_mock)
        self.assertIsNone(result)

    async def test_create_user(self):
        db_mock = self.session
        add_mock = self.session.add
        commit_mock = self.session.commit
        refresh_mock = self.session.refresh
        user_test = self.user_test

        # Create a dummy user payload
        user_payload = User(email='user1@example.com')

        # Call the create_user function
        new_user = await create_user(UserModel(**user_test.__dict__), db_mock)

        # Assert the expected behavior
        self.assertIsInstance(new_user, User)
        self.assertEqual(new_user.email, user_payload.email)
        self.assertEqual(new_user.username, user_test.username)
        self.assertEqual(new_user.email, user_test.email)
        self.assertEqual(new_user.password, user_test.password)
        self.assertNotEqual(new_user.avatar, "gravatar")
        self.assertEqual(new_user.refresh_token, None)

        self.session.add.assert_called_once_with(new_user)
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once()
        add_mock.assert_called_once_with(new_user)
        commit_mock.assert_called_once()
        refresh_mock.assert_called_once()

    async def test_update_token(self):
        user_test = self.user_test
        token = 'new token'

        self.session.commit = MagicMock()
        await update_token(user_test, token, self.session)

        self.assertEqual(user_test.refresh_token, token)
        self.session.commit.assert_called_once()

    async def test_confirmed_email(self):
        email = 'user1@example.com'

        user_mock = MagicMock(spec=User)
        user_mock.confirmed = True

        self.session.query().filter().one_or_none.return_value = user_mock
        self.session.commit = MagicMock()

        await confirmed_email(email, self.session)

        self.assertTrue(user_mock.confirmed)
        self.session.commit.assert_called_once()


if __name__ == '__main__':
    unittest.main()