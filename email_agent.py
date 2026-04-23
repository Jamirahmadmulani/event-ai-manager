import os
from flask_mail import Message
from models import db, EmailLog, User
from app import mail


def send_missing_fields_email(user_id, event_data):

    try:
        user = User.query.get(user_id)

        if not user:
            return

        missing_fields = []

        if not event_data.get("name"):
            missing_fields.append("Event Name")

        if not event_data.get("date"):
            missing_fields.append("Event Date")

        if not event_data.get("location"):
            missing_fields.append("Location")

        if not event_data.get("description"):
            missing_fields.append("Description")

        if not missing_fields:
            return

        subject = " Complete Your Event Details"

        body = f"""
Hello 

You started creating an event, but some details are missing.

 Missing Fields:
{', '.join(missing_fields)}

 Please login and update only these fields.

— Event AI Agent 
"""

        msg = Message(
            subject=subject,
            recipients=[user.email],
            sender=os.getenv("MAIL_USERNAME")
        )

        msg.body = body
        mail.send(msg)

        log = EmailLog(
            user_id=user_id,
            email=user.email,
            subject=subject,
            body=body
        )

        db.session.add(log)
        db.session.commit()

        print(" Email sent + stored")

    except Exception as e:
        print("EMAIL ERROR:", str(e))