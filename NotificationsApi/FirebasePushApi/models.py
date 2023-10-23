from django.db import models
from django.db import IntegrityError
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone
from firebase_admin.exceptions import *
from firebase_admin import messaging
from typing import Union, Optional, List
from django.utils import timezone
from datetime import datetime
import logging
import traceback

#initialize logger
db_logger = logging.getLogger('db')

#import FIREBASE_APP from settings
from NotificationsApi.settings import FIREBASE_APP 

# Create your models here.
class User(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('student', 'Student'),
        ('s_admin', 'Super Admin')
    )
    id = models.CharField(blank=False, max_length=25, db_index=True)
    email = models.CharField(max_length=255, blank=False, null=False,primary_key=True)
    user_type = ArrayField(models.CharField(blank=False, max_length=10, choices=ROLE_CHOICES), size=4, default=list, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    

    class Meta:
        ordering = ['created_at']
        verbose_name_plural = "User"
        unique_together = ('email', 'id')

    def __str__(self):
        return self.email

class Opening(models.Model):
    id=models.CharField(blank=False, max_length=25, db_index=True,primary_key=True)
    name=models.CharField(max_length=255, blank=False, null=False)
    deadline=models.DateTimeField(blank=False, null=False)
    notifications = models.JSONField(default=list, blank=True, null=True)
    role=models.CharField(max_length=255, blank=False, null=False)


#create A model to store firebase cloud messaging tokens
class FCMToken(models.Model):
    token = models.CharField(max_length=255, blank=False, null=False,primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tokens')
    
    class Meta:
        ordering = ['created_at']
        verbose_name_plural = "FCMToken"
    def save(self, *args, **kwargs):
        # Check if the user already has 3 tokens
        if self.user.tokens.count() >= 3:
            # Delete the last updated token
            last_updated_token = self.user.tokens.order_by('-last_updated').last()
            last_updated_token.delete()
        # Check if the token is already associated with a different user
        existing_token = FCMToken.objects.filter(token=self.token).exclude(user=self.user).first()
        if existing_token:
            # If the token is already associated with a different user, delete old entry
            # self.user = existing_token.user
            existing_token.delete()
        try:
            if not FCMToken.objects.filter(token=self.token,user=self.user).exists():
                super().save(*args, **kwargs)
                for user_type in self.user.user_type:
                    if user_type == 'admin':
                        topic_name = 'admins'
                    elif user_type == 'student':
                        topic_name = 'students'
                    elif user_type == 's_admin':
                        topic_name = 's_admins'
                    else:
                        # If the user has an unknown role, do not subscribe to any topic
                        continue

                # Subscribe the token to the appropriate topic
                    topic = f'/topics/{topic_name}'
                    response = messaging.subscribe_to_topic(self.token, topic, app=FIREBASE_APP)
                # Handle any errors that occur during subscription
                    if response.failure_count > 0:
                        print(response.errors)
                        db_logger.warning(response.errors)
                    # errors = [error for error in response.errors]
                    # self.deactivate_devices_with_error_results([self.token], errors)
                data = {
                    "title": "Welcome :)",
                    "body": "Thanks for subscribing to CDC Notifications",
                    "icon_url": "https://cdc.iitdh.ac.in/images/CDC_Logos/favicon.ico",
                    "url": "https://cdc.iitdh.ac.in/portal/" ,
                    }                   
                message = messaging.Message(
                    data=data,
                    token=self.token,
                )
                #  send a message to the user thanks for subscribing  if there are no errors 
                messaging.send(message, app=FIREBASE_APP)
            else:
                # If the token is already in the database, update the last_updated field of the existing token
                self.created_at=FCMToken.objects.get(token=self.token).created_at
                self.last_updated=datetime.now()
                super().save(*args, **kwargs)
                    
        except:
            print("Something went wrong")
            db_logger.error(traceback.format_exc())

    def send_message(self,message: messaging.Message,app: FIREBASE_APP,**more_send_message_kwargs) -> Union[Optional[messaging.SendResponse], FirebaseError]:
        message.token = self.token
        try:
            return messaging.SendResponse(
                {"name": messaging.send(message, app=app, **more_send_message_kwargs)},
                None,
            )
        except FirebaseError as e:
            self.deactivate_devices_with_error_result(self.token, e)
            return e

    def handle_topic_subscription(self,topic: str,app: FIREBASE_APP,should_subscribe: bool,**more_subscribe_kwargs) :
   
        try:
            _r_ids = [self.token]
            response = (
            messaging.subscribe_to_topic
            if should_subscribe
            else messaging.unsubscribe_from_topic
            )(_r_ids, topic, app=app, **more_subscribe_kwargs)
        except:
            print("Something went wrong")
            db_logger.error(traceback.format_exc())

    def deactivate_devices_with_error_result(self,registration_token: str, error: FirebaseError) -> None:
        """Deactivates devices with the given registration token and error."""
        # Check if the error was a registration error
        if isinstance(error, messaging.UnregisteredError):
            # Delete the token from the database
            FCMToken.objects.filter(token=registration_token).delete()
            print("Unregistered Token of user: "+self.user.email+" deleted")
        elif isinstance(error, UnavailableError):
            # If the error was an unavailable error, try again later
            pass
        elif isinstance(error, InternalError):
            # If the error was an internal error, try again later
            pass
        elif isinstance(error, InvalidArgumentError):
            # If the error was an invalid argument error, This is how new api reports error
            FCMToken.objects.filter(token=registration_token).delete()
            print("Invalid Token of user: "+self.user.email+" deleted")
        else:
            # If the error is unknown, log it
            db_logger.error(error)
            FCMToken.objects.filter(token=registration_token).delete()
            print("Unknown Token of user: "+self.user.email+" deleted")

   
    
    

    @staticmethod
    def send_topic_message(
        message: messaging.Message,
        topic_name: str,
        app: FIREBASE_APP,
        **more_send_message_kwargs,
    ) -> Union[Optional[messaging.SendResponse], FirebaseError]:
        message.topic = topic_name

        try:
            return messaging.SendResponse(
                {"name": messaging.send(message, app=app, **more_send_message_kwargs)},
                None,
            )
        except FirebaseError as e:
            db_logger.error(e)
            return e


    def __str__(self):
        return self.token

