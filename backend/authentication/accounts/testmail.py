import smtplib
from email.mime.text import MIMEText

smtp_server = "smtp.gmail.com"
port = 587
sender_email = "youssefichiba@gmail.com"
password = 'aehm cobk lhfd fevc'  # or App Password
receiver_email = "youssefichiba@gmail.com"  # Replace with your recipient email

message = MIMEText("This is a test email.")
message["Subject"] = "Test Email"
message["From"] = sender_email
message["To"] = receiver_email

try:
    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls()  # Upgrade the connection to secure
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email sent successfully")
except Exception as e:
    print(f"Error: {e}")
