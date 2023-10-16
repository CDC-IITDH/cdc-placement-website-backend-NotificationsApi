from rest_framework.response import Response
from rest_framework import status
import traceback
import json
from django.http import Http404
from django.shortcuts import get_object_or_404
from google.auth.transport import requests
from google.oauth2 import id_token
from django.utils import timezone
import os
from .models import *
import sys
from firebase_admin import messaging
from firebase_admin.messaging import Message, Notification
from datetime import datetime
import logging

#inialise logger
db_logger = logging.getLogger('db')


def precheck(required_data=None):
    if required_data is None:
        required_data = []

    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            try:
                request_data = None
                if request.method == 'GET':
                    request_data = request.GET
                elif request.method == 'POST':
                    request_data = request.data
                    if not len(request_data):
                        request_data = request.POST
                if len(request_data):
                    for i in required_data:
                        # print(i)
                        if i not in request_data:
                            return Response({'action': "Pre check", 'message': str(i) + " Not Found"},
                                            status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'action': "Pre check", 'message': "Message Data not Found"},
                                    status=status.HTTP_400_BAD_REQUEST)
                # print("Pre check: " + str(request_data))
                return view_func(request)
            except:
                # print what exception is
                print(traceback.format_exc())
                db_logger.warning("Pre check: " + str(sys.exc_info()))
                return Response({'action': "Pre check", 'message': "Something went wrong"},
                                status=status.HTTP_400_BAD_REQUEST)

        return wrapper_func

    return decorator


def isAuthorized(allowed_users=None):
    if allowed_users is None:
        allowed_users = []

    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            try:
                headers = request.META
                #print(headers)
                if 'HTTP_AUTHORIZATION' in headers:
                    token_id = headers['HTTP_AUTHORIZATION'][7:]
                    idinfo = id_token.verify_oauth2_token(token_id, requests.Request(), os.environ.get('GOOGLE_OAUTH_CLIENT_ID'))
                    email = idinfo["email"]
                    print(idinfo)
                    user = get_object_or_404(User, email=email)
                    if user:
                        user.last_login_time = timezone.now()
                        user.save()
                        if len(set(user.user_type).intersection(set(allowed_users))) or allowed_users == '*':
                            if "MODIFIED" in headers:
                                return view_func(request, user.id, user.email, user.user_type, token_id, *args,
                                                 **kwargs)
                            else:
                                return view_func(request, user.id, user.email, user.user_type, *args, **kwargs)
                        else:
                            raise PermissionError("Access Denied. You are not allowed to use this service")
                else:
                    raise PermissionError("Authorization Header Not Found")

            except PermissionError:
                print(sys.exc_info())
                db_logger.warning("Is Authorized? " + str(sys.exc_info()))
                return Response({'action': "Is Authorized?", 'message': 'Access Denied'},
                                status=status.HTTP_401_UNAUTHORIZED)
            except Http404:
                print(sys.exc_info())
                db_logger.warning("Is Authorized? " + str(sys.exc_info()))
                return Response({'action': "Is Authorized?", 'message': "User Not Found. Contact CDC for more details"},
                                status=status.HTTP_404_NOT_FOUND)
            except ValueError as e:
                print(sys.exc_info())
                db_logger.error("Problem with Google Oauth2.0 " + str(sys.exc_info()))
                # logger.error("Problem with Google Oauth2.0 " + str(e))
                return Response({'action': "Is Authorized?", 'message': 'Problem with Google Sign In'},
                                status=status.HTTP_401_UNAUTHORIZED)
            except:
                print(sys.exc_info())
                db_logger.warning("Is Authorized? " + str(sys.exc_info()))
                return Response(
                    {'action': "Is Authorized?", 'message': "Something went wrong. Contact CDC for more details"},
                    status=status.HTTP_400_BAD_REQUEST)

        return wrapper_func

    return decorator

    
def send_notifications(opening):
    try:
     
        topic="students"
        deadline=opening.deadline
        name=opening.name
        role=opening.role
        # Calculate time differences
        time_diff = deadline - datetime.now()
        days_diff = time_diff.days
        hours_diff = time_diff.seconds // 3600
        minutes_diff = (time_diff.seconds // 60) % 60
        Notification_no=0
        # Set custom messages based on time differences
        if days_diff ==0 and hours_diff>23 :
            message = f"It's high time to apply for the role before {deadline}. You have less than 24 hrs left."
            Notification_no=1
        elif hours_diff > 5 and hours_diff<=6 :
            message = f"It's high time to apply for the role before {deadline}. You have less than {hours_diff} hours left."
            Notification_no=2
        elif hours_diff >2 and hours_diff<=3 :
            message = f"Hurry up! The deadline to apply for the role is {deadline}. You have less than {hours_diff} hours left."
            Notification_no=3
        # elif hours_diff > 0 and hours_diff<=1:
        #     message = f"Last chance to apply for the role! The deadline is {deadline}. You have less than {hours_diff} hours left."
        #     Notification_no=4
        elif minutes_diff > 30 and minutes_diff<=60:
            message = f"Time is running out! The deadline to apply for the role is {deadline}. You have less than 1 hr left."
            Notification_no=4
        elif minutes_diff <=30:
            message = f"The deadline to apply for the role is {deadline}. You have less than 30 minutes left!"
            Notification_no=5
        
        if Notification_no!=0 and Notification_no not in opening.notifications:

            data = {
                "title": name+" - "+role,
                "body": message,
                "icon_url": "https://cdc.iitdh.ac.in/images/CDC_Logos/favicon.ico",
                "url": "https://cdc.iitdh.ac.in/portal/",
                }
        
            FCMToken.send_topic_message(Message(
                data=data,
                ),topic_name=topic,app=FIREBASE_APP)
            
            opening.notifications[Notification_no]=True
            opening.save()
            

        
    except:
        # print what exception is
        db_logger.error(traceback.format_exc())
        print("Something went wrong while sending remainder notifications")        
       
    
