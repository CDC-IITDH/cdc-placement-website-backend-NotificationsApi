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
                    send_mails_opening(opening.id)
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


def populate_notification_panel():
    try:
        print("Populating notification panel at "+str(datetime.now()))
        for user in User.objects.all():
            user.notification_panel=[]
            user.save()
        openings=Opening.objects.all()
        for opening in openings:
            deadline=opening.deadline
            if(deadline>timezone.now() and deadline-timezone.now()<timezone.timedelta(days=1)):
                print("Populating notification panel for "+str(opening.id))
                try:
                    header=jwt.encode({"typ":"JWT","alg":"HS256","kid":"1","send_all":"True"},os.environ.get("JWT_SECRET_KEY"),algorithm="HS256")
                    headers={"Authorization":"Bearer "+header}
                    url = os.environ.get("BACKEND_FETCH_API_URL")+"?opening_id="+str(opening.id)+"&send_all=True"
                    payload = {}
                    resp = rq.request("GET", url, headers=headers, data=payload)
                    res=json.loads(resp.text)
                    if(resp.status_code!=200):
                            print("Something went wrong while populating remainder notifications")
                            db_logger.error("Something went wrong while populating remainder notifications"+str(resp))
                    else:
                        if not res["eligible_students"][0]:
                            print("No one is eligible for opening at " +opening.name)
                            continue
                        print("Eligible students for opening at "+opening.name)
                        eligible_students=res["eligible_students"][1]
                        for student in eligible_students:
                            print(student)
                            try:
                                user=User.objects.get(email=student)
                                user.notification_panel.append({"type":"opening","id":opening.id,"name":opening.name,"timing":str(opening.deadline)})
                                user.save()
                            except:
                                db_logger.error(traceback.format_exc())
                                print("Something went wrong while populating notification panel")
                    
                   
                except:
                    db_logger.error(traceback.format_exc())
                    print("Something went wrong while populating notification panel")

        for event in Event.objects.all():
            date=event.date
            if(date==timezone.localdate()):
                print("Populating notification panel for "+str(event.id))
                try:
                   for user in event.registered_users.all():
                        try:
                            user.notification_panel.append({"type":"event","id":event.id,"name":event.name,"timing":event.timing})
                            user.save()
                        except:
                            db_logger.error(traceback.format_exc())
                            print("Something went wrong while populating notification panel")
                   
                except:
                    db_logger.error(traceback.format_exc())
                    print("Something went wrong while populating notification panel")
    except:
        db_logger.error(traceback.format_exc())
        print("Something went wrong while populating notification panel")
