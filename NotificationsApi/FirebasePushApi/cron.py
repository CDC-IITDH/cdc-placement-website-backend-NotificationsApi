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

