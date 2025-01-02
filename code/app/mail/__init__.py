import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(smtp_server, smtp_port, subject, body, to_emails, from_email, password):
    """
    Send an email using Office 365 SMTP server with authentication.

    :param subject: Subject of the email
    :param body: Body of the email
    :param to_emails: Recipient email address
    :param from_email: Sender email address
    :param password: Password for SMTP authentication
    """
    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = ", ".join(to_emails)
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(from_email, password)
            server.sendmail(from_email, to_emails, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error: {e}")