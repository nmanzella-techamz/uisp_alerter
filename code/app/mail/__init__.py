import smtplib
from datetime import timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from textwrap import dedent

from helpers import timedelta_to_human_readable


def send_email(subject, body, to_emails, from_email, password):
    """
    Send an email using Office 365 SMTP server with authentication.

    :param subject: Subject of the email
    :param body: Body of the email
    :param to_emails: Recipient email address
    :param from_email: Sender email address
    :param password: Password for SMTP authentication
    """
    smtp_server = "smtp.office365.com"
    smtp_port = 587
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


def send_uisp_alert(
    alerts: list[str],
    site_name: str,
    to_emails: list[str],
    from_email: str,
    password: str,
    timezone: str,
    time_span: timedelta,
):
    total = len(alerts)
    subject = f"{total} Alert{'s'[:total^1]} for {site_name} UISP Devices"
    body_start = dedent(f"""\
    {total} alert{'s'[:total^1]} from UISP devices at {site_name} in the last {timedelta_to_human_readable(time_span)}.\n
    Times below are in the "{timezone}" timezone.\n
    """)
    body = body_start + "\n".join(alerts)
    send_email(subject, body, to_emails, from_email, password)
