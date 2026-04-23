import imaplib
import email
from models import db, Event, User
from email.utils import parseaddr


def read_email_replies():
    print(" Reading emails...")

    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")

        
        mail.login("jamirahmadmulani8@gmail.com", "nqdauwwjnnmzxygu")

        mail.select("inbox")

        status, messages = mail.search(None, '(UNSEEN)')

        #  no emails safety
        if not messages or not messages[0]:
            print("No new emails")
            return

        for num in messages[0].split():
            _, msg_data = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])

            from_email = parseaddr(msg.get("from", ""))[1]
            subject = msg.get("subject", "")

            if not from_email:
                continue

            from_email = from_email.strip().lower()

            print("From:", from_email)
            print(" Subject:", subject)

           
            #  SPAM FILTER (IMPORTANT)
            
            if "best-jobs-online.com" in from_email:
                print(" Spam email skipped")
                continue

          
            # BODY EXTRACTION SAFE
           
            body = ""

            try:
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            payload = part.get_payload(decode=True)
                            if payload:
                                body = payload.decode(errors="ignore")
                                break
                else:
                    payload = msg.get_payload(decode=True)
                    if payload:
                        body = payload.decode(errors="ignore")
            except:
                body = ""

            print(" Body:", body)

            
            #  FIND USER
            
            user = User.query.filter(User.email.ilike(from_email)).first()

            if not user:
                print(" User not found:", from_email)
                continue

            
            # GET LAST EVENT
            
            event = Event.query.filter_by(created_by=user.id) \
                               .order_by(Event.id.desc()) \
                               .first()

            if not event:
                print("No event found")
                continue

            
            #  UPDATE EVENT SAFELY
            
            text = body.lower()

            try:
                if "description:" in text:
                    event.description = body.lower().split("description:")[1].split("\n")[0].strip()

                if "location:" in text:
                    event.location = body.lower().split("location:")[1].split("\n")[0].strip()

                db.session.commit()
                print(" Event updated successfully")

            except Exception as e:
                print("Update error:", str(e))
                db.session.rollback()

    except Exception as e:
        print("FATAL ERROR:", str(e))