import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

gmail_user = os.getenv("GMAIL_USER")
gmail_pass = os.getenv("GMAIL_PASS")

print(f"Sending from: {gmail_user}")

msg = MIMEMultipart()
msg['From'] = gmail_user
msg['To'] = gmail_user  # sending to yourself as a test
msg['Subject'] = "JARVIS Test Email"
msg.attach(MIMEText("This is a test email from JARVIS!", 'plain'))

try:
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(gmail_user, gmail_pass)
    server.sendmail(gmail_user, gmail_user, msg.as_string())
    server.quit()
    print("✅ Email sent successfully!")
except Exception as e:
    print(f"❌ Error: {e}")
