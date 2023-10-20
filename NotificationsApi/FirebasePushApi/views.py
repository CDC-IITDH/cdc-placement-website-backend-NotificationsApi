from .utils import *
from .models import *
from firebase_admin.messaging import Message, Notification
import jwt
import os
import traceback
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from datetime import datetime
import logging

#inialise logger
db_logger = logging.getLogger('db')

@api_view(['POST'])

@precheck(['fcm_token'])
@isAuthorized(allowed_users='*')
def add_FCMToken(request,id,email,user_type):
    try:
        user=get_object_or_404(User,email=email)
        fcm_token = request.data['fcm_token']
        fcmtoken=FCMToken()
        fcmtoken.token=fcm_token
        fcmtoken.user=user
        fcmtoken.save()


        return Response({'action': "Add FCM Token", 'message': "FCM Token Added"},
                        status=status.HTTP_200_OK)
    except Http404:
        return Response({'action': "Add FCM Token", 'message': "User not found"},
                        status=status.HTTP_404_NOT_FOUND)
    except:
        # print what exception is
      #  print(traceback.format_exc())
        db_logger.warning("Add FCM Token: " + str(sys.exc_info()))
        return Response({'action': "Add FCM Token", 'message': "Something went wrong"},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@precheck(['token'])
def send(request):
    try:
        token = request.data['token']
       # jwt.decode
        decoded_token = jwt.decode(token, os.environ.get("JWT_SECRET_KEY"), algorithms=['HS256'])
        title=decoded_token['title']
        body=decoded_token['body']
        url=decoded_token['url']
        
            
        data = {
            "title": title,
            "body": body,
            "icon_url": "https://cdc.iitdh.ac.in/images/CDC_Logos/favicon.ico",
            "url": "https://cdc.iitdh.ac.in/portal/" if url=="" else url,
        }
        if "topic" in decoded_token:
            topic=decoded_token['topic']
            FCMToken.send_topic_message(Message(
                data=data,
            ),topic_name=topic,app=FIREBASE_APP)
            return Response({'action': "Send Notification", 'message': "Notification Sent"},
                        status=status.HTTP_200_OK)

        elif "email" in decoded_token:
            email=decoded_token['email']
            user=get_object_or_404(User,email=email)
            tokens=FCMToken.objects.filter(user=user)
            for token in tokens:
                token.send_message(Message(
                    data=data,
                ),app=FIREBASE_APP)
            return Response({'action': "Send Notification", 'message': "Notification Sent"},
                        status=status.HTTP_200_OK)


        
    except:
        # print what exception is
        db_logger.warning("Send Notification: " + str(sys.exc_info()))
        return Response({'action': "Send Notification", 'message': "Something went wrong"},
                        status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['POST'])
@precheck(['token'])
def add_opening(request):
    try:
        token=request.data['token']
        decoded_token = jwt.decode(token, os.environ.get("JWT_SECRET_KEY"), algorithms=['HS256'])
        name=decoded_token['company']
        deadline=decoded_token['deadline']
        role=decoded_token['role']
        id=decoded_token['id']
        deadline = datetime.strptime(deadline, '%Y-%m-%d %H:%M:%S %z')
        if(Opening.objects.filter(id=id).exists()):
            if(Opening.objects.filter(id=id).update(name=name,deadline=deadline,role=role,notifications=[])):
                return Response({'action': "Add Opening", 'message': "Opening Updated"},
                        status=status.HTTP_200_OK)
            return Response({'action': "Add Opening", 'message': "Opening already exists"},
                        status=status.HTTP_400_BAD_REQUEST)
        
        Opening.objects.create(id=id,name=name,deadline=deadline,role=role)
        return Response({'action': "Add Opening", 'message': "Opening Added"},
                        status=status.HTTP_200_OK)
    except:
        # print what exception is
        db_logger.warning("Add Opening: " + str(sys.exc_info()))
        return Response({'action': "Add Opening", 'message': "Something went wrong"},
                        status=status.HTTP_400_BAD_REQUEST)