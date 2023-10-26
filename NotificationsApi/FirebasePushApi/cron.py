import logging
from .models import *
from .utils import *
import traceback
from datetime import datetime
db_logger = logging.getLogger('db')

def send_remainder_notifications():
    try:
        print("Sending notifications at "+str(datetime.now()))
        openings=Opening.objects.all()
        for opening in openings:
            deadline=opening.deadline
            if(deadline>timezone.now()):
                print("Sending notification for "+str(opening.id))
                try:
                    send_notifications(opening)
                except:
                    db_logger.error(traceback.format_exc())
                    print("Something went wrong while sending notifications")

    except:
        db_logger.error(traceback.format_exc())
        print("Something went wrong while sending notifications")

def send_remainder_mails():
    try:
        print("Sending mails at "+str(datetime.now()))
        openings=Opening.objects.all()
        for opening in openings:
            deadline=opening.deadline
            if(deadline>timezone.now() and deadline-timezone.now()<timezone.timedelta(days=1)):
                print("Sending mail for "+str(opening.id))
                try:
                    send_mails_opening(opening)
                except:
                    db_logger.error(traceback.format_exc())
                    print("Something went wrong while sending mails")

    except:
        db_logger.error(traceback.format_exc())
        print("Something went wrong while sending mails")

def ordinal(number):
    if 10 <= number % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(number % 10, 'th')
    return  suffix

# Format the date as "22nd May"

def send_daily_digest():
    try:
        print("Sending daily digest at "+str(datetime.now()))
        openings=Opening.objects.all()
        data={
            "events":[], #list of events
        }
        date=timezone.localdate()
        formatted_date = date.strftime("%d") + ordinal(date.day) + " " + date.strftime("%B")
        print(formatted_date)
        for opening in openings:
            deadline=opening.deadline
            if(deadline>timezone.now() and deadline-timezone.now()<timezone.timedelta(days=1)):
                data["events"].append((opening.name+'-'+opening.role,"Deadline",formatted_date,deadline.strftime("%I:%M %p")))
        for event in Event.objects.all():
            date=event.date
            if(date==timezone.localdate()):
                data["events"].append((event.name,event.description,formatted_date,event.timing))
        students=User.objects.all()
        mails=[]
        for student in students:
            mails.append(student.email)
        try:
            sendEmail(mails,"CDC-Daily Digest-"+formatted_date,data,"daily_digest.html")
        except:
            db_logger.error(traceback.format_exc())
            print("Something went wrong while sending digest mails")

    except:
        db_logger.error(traceback.format_exc())
        print("Something went wrong while sending digest mails")

