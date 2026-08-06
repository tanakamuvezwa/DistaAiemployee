import os
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class RealGmailService:
    """
    Real Gmail Integration Service
    Supports IMAP email fetching, SMTP email sending, and credential management.
    Uses standard Gmail App Passwords or OAuth credentials.
    """

    def __init__(self):
        # Credentials loaded from environment or config file
        self.email_address = os.environ.get("GMAIL_ADDRESS", "")
        self.app_password = os.environ.get("GMAIL_APP_PASSWORD", "")
        self.imap_server = "imap.gmail.com"
        self.smtp_server = "smtp.gmail.com"

    def is_configured(self) -> bool:
        return bool(self.email_address and self.app_password)

    def set_credentials(self, address: str, password: str):
        self.email_address = address.strip()
        self.app_password = password.strip()
        os.environ["GMAIL_ADDRESS"] = self.email_address
        os.environ["GMAIL_APP_PASSWORD"] = self.app_password

    def fetch_unread_emails(self, max_results=5):
        """Fetch real unread emails from Gmail IMAP inbox"""
        if not self.is_configured():
            return []

        try:
            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.email_address, self.app_password)
            mail.select("inbox")

            status, response = mail.search(None, "UNSEEN")
            if status != "OK":
                mail.logout()
                return []

            email_ids = response[0].split()
            unread_emails = []

            # Fetch newest emails up to max_results
            for e_id in reversed(email_ids[-max_results:]):
                res, msg_data = mail.fetch(e_id, "(RFC822)")
                if res != "OK":
                    continue

                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject = msg.get("Subject", "(No Subject)")
                        sender = msg.get("From", "Unknown")
                        date_str = msg.get("Date", "")

                        # Extract body text
                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain":
                                    body = part.get_payload(decode=True).decode(errors="ignore")
                                    break
                        else:
                            body = msg.get_payload(decode=True).decode(errors="ignore")

                        unread_emails.append({
                            "sender": sender,
                            "subject": subject,
                            "body": body[:300] + ("..." if len(body) > 300 else ""),
                            "date": date_str,
                            "priority": "HIGH" if "urgent" in subject.lower() or "important" in subject.lower() else "ACTION"
                        })

            mail.logout()
            return unread_emails

        except Exception as e:
            print(f"[Gmail Error] IMAP fetch failed: {e}")
            return []

    def send_real_email(self, to_address: str, subject: str, body_text: str) -> dict:
        """Send a real email via Gmail SMTP"""
        if not self.is_configured():
            return {
                "success": False,
                "message": "Gmail is not configured. Please add your Gmail Address & App Password in Dista AI Settings."
            }

        try:
            msg = MIMEMultipart()
            msg["From"] = self.email_address
            msg["To"] = to_address
            msg["Subject"] = subject
            msg.attach(MIMEText(body_text, "plain"))

            with smtplib.SMTP_SSL(self.smtp_server, 465) as server:
                server.login(self.email_address, self.app_password)
                server.sendmail(self.email_address, to_address, msg.as_string())

            return {
                "success": True,
                "message": f"Real email sent successfully to {to_address} via Gmail!"
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"SMTP Error sending email: {str(e)}"
            }

gmail_service = RealGmailService()
