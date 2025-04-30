import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
TO_EMAIL = os.getenv("RECEIVER_EMAIL")


triggered_emails = set()

def send_handoff_email(message_text, user_name="Website Visitor", user_phone="N/A"):
 
    message_hash = hash((user_name, message_text))
    if message_hash in triggered_emails:
        
        return

    
    msg = EmailMessage()
    msg["Subject"] = "🔔 User Requested a Consultant"
    msg["From"] = EMAIL_USER
    msg["To"] = TO_EMAIL
    msg.set_content(f"""A user has asked to speak with a consultant.

Name: {user_name}
Phone: {user_phone}
Message: {message_text}
""")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)

        triggered_emails.add(message_hash)

    
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
