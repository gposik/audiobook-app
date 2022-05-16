import os
from typing import List
from requests import Response, post

FAILED_LOAD_DOMAIN = "Failed to load domain."
FAILED_LOAD_API_KEY = "Failed to load API key."
ERROR_SENDING_EMAIL = "Error in sending email, please try again."


class MailgunException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class Mailgun:
    MAILGUN_DOMAIN = os.environ.get("MAILGUN_DOMAIN")
    MAILGUN_API_KEY = os.environ.get("MAILGUN_API_KEY")
    FROM_EMAIL = os.environ.get("SENDER_EMAIL")
    FROM_TITLE = "Audiobook Builder"

    @classmethod
    def send_email(
        cls, email: List[str], subject: str, text: str, html: str
    ) -> Response:
        if cls.MAILGUN_DOMAIN is None:
            raise MailgunException(FAILED_LOAD_DOMAIN)

        if cls.MAILGUN_API_KEY is None:
            raise MailgunException(FAILED_LOAD_API_KEY)

        response = post(
            f"https://api.mailgun.net/v3/{cls.MAILGUN_DOMAIN}/messages",
            auth=("api", cls.MAILGUN_API_KEY),
            data={
                "from": f"{cls.FROM_TITLE} <{cls.FROM_EMAIL}>",
                "to": email,
                "subject": subject,
                "text": text,
                "html": html,
            },
        )

        if response.status_code != 200:
            raise MailgunException(ERROR_SENDING_EMAIL)

        return response
