import asyncio

from fastapi_mail import FastMail

from src.services.auth import auth_service
from src.services.email import send_email


def test_send_email(monkeypatch):
    async def mock_send_message(self, message, template_name):
        assert message.recipients == ['test@example.com']
        assert message.subject == 'Confirm your email!'
        assert message.template_body == {
            "host": "example.com",
            "username": "testuser",
            "token": "mocked_token"
        }
        assert template_name == "email_template.html"

    monkeypatch.setattr(FastMail, "send_message", mock_send_message)

    monkeypatch.setattr(
        auth_service,
        "create_email_token",
        lambda payload: "mocked_token"
    )

    asyncio.run(send_email("test@example.com", "testuser", "example.com"))