import os
import smtplib
import logging
from typing import List, Dict, Any
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
        self._template_base = self._get_base_template()

    def send_ipo_notification(self, recipients: List[str], new_ipos: List[Any]) -> bool:
        """
        Sends a notification email to recipients with the list of new IPOs.
        
        Args:
            recipients: List of email addresses to send to.
            new_ipos: List of IPO objects (or dicts) containing company details.
            
        Returns:
            bool: True if email was sent to at least one recipient, False otherwise.
        """
        if not new_ipos:
            logger.info("No new IPOs to notify about.")
            return False

        subject = f"New IPO Alert: {len(new_ipos)} New Opportunit{'y' if len(new_ipos) == 1 else 'ies'} Detected"
        
        try:
            html_content = self._build_email_content(new_ipos)
            return self._send_bulk_email(recipients, subject, html_content)
        except Exception as e:
            logger.error(f"Failed to prepare or send IPO notification: {e}")
            return False

    def _build_email_content(self, ipos: List[Any]) -> str:
        """Constructs the full HTML email body."""
        ipo_rows_html = ""
        for ipo in ipos:
            ipo_rows_html += self._format_ipo_row(ipo)

        # Inject the rows into the base template
        return self._template_base.replace("{ipo_list_content}", ipo_rows_html)

    def _format_ipo_row(self, ipo: Any) -> str:
        """Formats a single IPO object into an HTML table row/block."""
        # Handle both Django model objects and dictionaries
        company_name = getattr(ipo, 'company_name', None) or ipo.get('company_name', 'Unknown Company')
        share_type = getattr(ipo, 'share_type', None) or ipo.get('share_type', 'IPO')
        raw_share_group = getattr(ipo, 'share_group', None) or ipo.get('share_group', '')
        
        # Extract symbol if share_group looks like "(SYMBOL)"
        symbol = "-"
        share_group = raw_share_group
        
        if raw_share_group.startswith('(') and raw_share_group.endswith(')'):
            symbol = raw_share_group[1:-1]
        
        return f"""
        <table width="100%" cellpadding="0" cellspacing="0" role="presentation" style="
                border:1px solid #e5e7eb;
                border-radius:6px;
                background:#fafbfc;
                margin-bottom: 16px;
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
                            {share_type}
                        </span>
                    </p>

                    <p style="
                            margin:8px 0 0;
                            font-size:13px;
                            color:#6b7280;
                        ">
                        Ordinary Shares • {share_group} • NEPSE
                    </p>
                </td>
            </tr>
        </table>
        """

    def _send_bulk_email(self, recipients: List[str], subject: str, html_body: str) -> bool:
        """Sends the constructed email to a list of recipients."""
        if not recipients:
            return False
            
        msg = MIMEMultipart()
        msg['From'] = f"{self.sender_name} <{self.sender_email}>"
        msg['Subject'] = subject
        msg.attach(MIMEText(html_body, 'html'))

        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            
            success_count = 0
            for recipient in recipients:
                try:
                    msg.replace_header('To', recipient) if 'To' in msg else msg.add_header('To', recipient)
                    
                    server.sendmail(self.sender_email, recipient, msg.as_string())
                    logger.info(f"Email sent successfully to {recipient}")
                    success_count += 1
                except Exception as inner_e:
                    logger.error(f"Failed to send to {recipient}: {inner_e}")

            server.quit()
            return success_count > 0

        except Exception as e:
            logger.error(f"Failed to connect to SMTP server: {e}")
            return False

    def _get_base_template(self) -> str:
        return """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    @media only screen and (max-width: 600px) {
                        .container { width: 100% !important; }
                    }
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
                                        <p style="margin:0 0 16px;font-size:15px;">Dear Investor,</p>
                                        <p style="margin:0 0 22px;font-size:15px;">
                                            New investment opportunities have been announced in the Nepal Stock Exchange (NEPSE).
                                            Below are the key details:
                                        </p>

                                        <!-- DYNAMIC CONTENT START -->
                                        {ipo_list_content}
                                        <!-- DYNAMIC CONTENT END -->

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
                                            This is a notification-only address.
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

if __name__ == "__main__":
    email_service = EmailService()
    
    test_ipos = [
        {
            "company_name": "Test Hydropower Ltd.",
            "share_type": "IPO",
            "share_group": "(THL)"
        },
        {
            "company_name": "Another Finance Co.",
            "share_type": "FPO",
            "share_group": "Finance"
        }
    ]
    
    email_service.send_ipo_notification(
        recipients=["anmoldkl971@gmail.com"],
        new_ipos=test_ipos
    )
