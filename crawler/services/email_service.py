import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

load_dotenv()

class EmailService:
    def __init__(self):
        self.smtp_server = "smtp-relay.brevo.com"
        self.smtp_port = 587
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.sender_email = "no-reply@newspluk.com"
        self.sender_name = "Mero-Lagani Team"

    def get_template(self):
        return """
            <!DOCTYPE html>
            <html>

            <head>
                <meta charset="UTF-8">
                <style>
                    @media only screen and (max-width: 600px) {{
                        .container {{
                            width: 100% !important;
                        }}
                    }}
                </style>
            </head>

            <body style="margin:0;padding:0;font-family:Helvetica,Arial,sans-serif;background:#f2f4f7;">

                <table width="100%" cellpadding="0" cellspacing="0" role="presentation" style="padding:20px;">
                    <tr>
                        <td align="center">

                            <table class="container" width="600" cellpadding="0" cellspacing="0" role="presentation" style="
                                    background:#ffffff;
                                    border-radius:8px;
                                    box-shadow:0 3px 8px rgba(0,0,0,0.08);
                                    overflow:hidden;
                                ">

                                <tr>
                                    <td style="
                                            background:#0b5ed7;
                                            padding:18px 24px;
                                            text-align:center;
                                        ">
                                        <h1 style="
                                                margin:0;
                                                color:#ffffff;
                                                font-size:22px;
                                                font-weight:600;
                                            ">
                                            Mero Lagani — IPO Alert
                                        </h1>
                                    </td>
                                </tr>

                                <tr>
                                    <td style="padding:28px;color:#1f2933;">

                                        <p style="margin:0 0 16px;font-size:15px;">
                                            Dear Investor,
                                        </p>

                                        <p style="margin:0 0 22px;font-size:15px;">
                                            A new IPO has been announced in the Nepal Stock Exchange (NEPSE).
                                            Below are the key details:
                                        </p>

                                        <table width="100%" cellpadding="0" cellspacing="0" role="presentation" style="
                                                border:1px solid #e5e7eb;
                                                border-radius:6px;
                                                background:#fafbfc;
                                            ">
                                            <tr>
                                                <td style="padding:18px;">

                                                    <p style="
                                                            margin:0;
                                                            font-size:17px;
                                                            font-weight:600;
                                                            color:#111827;
                                                        ">
                                                        {company_name}
                                                        <span style="
                                                                font-weight:500;
                                                                color:#6b7280;
                                                            ">
                                                            ({symbol})
                                                        </span>

                                                        <span style="
                                                                display:inline-block;
                                                                background:#0b5ed7;
                                                                color:#ffffff;
                                                                font-size:11px;
                                                                font-weight:600;
                                                                padding:4px 8px;
                                                                border-radius:4px;
                                                                margin-left:8px;
                                                                vertical-align:middle;
                                                            ">
                                                            {ipo_type}
                                                        </span>
                                                    </p>

                                                    <p style="
                                                            margin:8px 0 0;
                                                            font-size:13px;
                                                            color:#6b7280;
                                                        ">
                                                        Ordinary Shares • {market_type} • NEPSE
                                                    </p>

                                                </td>
                                            </tr>
                                        </table>

                                        <p style="margin:22px 0 0;font-size:15px;">
                                            Please review the prospectus and application schedule before investing.
                                            Mero Lagani will continue to notify you of important market opportunities.
                                        </p>

                                        <p style="margin-top:26px;font-size:15px;">
                                            Regards,<br>
                                            <strong>Mero Lagani Team</strong>
                                        </p>

                                    </td>
                                </tr>

                                <tr>
                                    <td style="
                                            background:#f5f7fa;
                                            padding:18px;
                                            text-align:center;
                                            border-top:1px solid #e5e7eb;
                                        ">

                                        <p style="
                                                font-size:11px;
                                                color:#7b8794;
                                                margin:0 0 6px;
                                            ">
                                            This email was sent to {user_email}. This is a notification-only address.
                                        </p>

                                        <p style="
                                                font-size:11px;
                                                color:#7b8794;
                                                margin:0;
                                            ">
                                            &copy; 2025 Mero Lagani — Kathmandu, Nepal
                                        </p>

                                    </td>
                                </tr>

                            </table>

                        </td>
                    </tr>
                </table>

            </body>

            </html>
        """

    def send_email(self, to_email, subject, context):
        template_content = self.get_template()
        if not template_content:
            return False

        try:
            if 'user_email' not in context:
                context['user_email'] = to_email
                
            body_html = template_content.format(**context)
        except KeyError as e:
            logger.error(f"Missing placeholder in context: {e}")
            return False
        except Exception as e:
            logger.error(f"Error formatting template: {e}")
            return False

        msg = MIMEMultipart()
        msg['From'] = f"{self.sender_name} <{self.sender_email}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body_html, 'html'))

        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.sendmail(self.sender_email, to_email, msg.as_string())
            server.quit()
            logger.info(f"Email sent successfully to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

if __name__ == "__main__":
    email_service = EmailService()
    
    test_context = {
        "company_name": "Test Company Ltd.",
        "symbol": "TEST",
        "ipo_type": "IPO",
        "sector": "Hydropower",
        "market_type": "Primary Market",
        "user_email": "anmoldkl971@gmail.com"
    }
    
    email_service.send_email(
        to_email="anmoldkl971@gmail.com",
        subject="IPO Now Open – Don’t Miss This Investment Opportunity",
        context=test_context
    )