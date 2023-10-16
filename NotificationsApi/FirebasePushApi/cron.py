
from .models import *
from .utils import *
import traceback
def send_remainder_notifications():
    try:
        print("Sending notifications")
        openings=Opening.objects.all()
        for opening in openings:
            deadline=opening.deadline
            if(deadline>datetime.now()):
                try:
                    send_notifications(opening)
                except:
                    print(traceback.format_exc())
                    print("Something went wrong")

    except:
        print(traceback.format_exc())
        print("Something went wrong")
