import resend

from app.core.logger import setup_logger

resend.api_key = "re_gsA2vW5q_7xMByJVWybKzPe8oYEPojDGt"

logger = setup_logger(__name__)


class EmailService:

    @staticmethod
    def send_email(email: str):
        params: resend.Emails.SendParams = {
            "from": "onboarding@resend.dev",
            "to": email,
            "subject": "Hello World",
            "html": "<p>Congrats on sending your <strong>first email</strong>!</p>"
        }
        email = resend.Emails.send(params)
        logger.info(f"Email sent successfully to {email}")
