import resend
from pydantic import EmailStr

from app.core.logger import setup_logger
from app.dtos.ticket_dto import TicketDTO

resend.api_key = "re_gsA2vW5q_7xMByJVWybKzPe8oYEPojDGt"

logger = setup_logger(__name__)

import resend
from pydantic import EmailStr
from typing import List

class EmailService:
    @staticmethod
    def send_email(email: EmailStr, tickets: List['TicketDTO']):  # Assuming qr_code is now a Base64 string

        # 1. Build the dynamic ticket blocks
        tickets_html = ""
        for ticket in tickets:
            tickets_html += f"""
            <div style="border: 2px dashed #cccccc; border-radius: 8px; padding: 20px; margin-bottom: 20px; text-align: center; background-color: #f9f9f9; max-width: 400px; margin-left: auto; margin-right: auto;">
                <p style="color: #666666; font-size: 14px;"><strong>Ticket ID:</strong><br>{ticket.uuid}</p>
                <p style="color: #666666; font-size: 14px;"><strong>Event ID:</strong><br>{ticket.event_uuid}</p>

                <img src="data:image/png;base64,{ticket.qr_code}" alt="Ticket QR Code" style="width: 200px; height: 200px; margin: 15px 0; border: 1px solid #eeeeee; border-radius: 4px;" />

                <p style="color: #999999; font-size: 12px; margin-bottom: 0;">Present this QR code at the entrance.</p>
            </div>
            """

        # 2. Wrap it in the main HTML layout
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: Arial, sans-serif; background-color: #ffffff; padding: 20px; margin: 0;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eaeaec; border-radius: 10px;">
                <h2 style="color: #111111; text-align: center;">Your Event Tickets</h2>
                <p style="color: #555555; text-align: center; margin-bottom: 30px;">
                    Thank you for your order! Your tickets are below.
                </p>

                {tickets_html}

                <hr style="border: none; border-top: 1px solid #eeeeee; margin: 30px 0;" />
                <p style="color: #888888; font-size: 12px; text-align: center;">
                    Order Ref: {tickets[0].order_uuid if tickets else 'N/A'}
                </p>
            </div>
        </body>
        </html>
        """

        # 3. Send the email
        params: resend.Emails.SendParams = {
            "from": "Tickets <onboarding@resend.dev>",
            "to": "nikoskoutsoukosprelorentzos@gmail.com",
            "subject": "Your Event Tickets",
            "html": full_html
        }

        try:
            response = resend.Emails.send(params)
            logger.info(f"Email sent successfully to {email}")
            return response
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            raise e