from django.db import models
from django.db import IntegrityError
from django.utils import timezone
from firebase_admin.exceptions import FirebaseError, InvalidArgumentError
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
    user_type = models.CharField(max_length=7, choices=ROLE_CHOICES, blank=False, null=False)
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
            super().save(*args, **kwargs)
            if self.user.user_type == 'admin':
              topic_name = 'admins'
            elif self.user.user_type == 'student':
              topic_name = 'students'
            elif self.user.user_type == 's_admin':
                topic_name = 's_admins'
            else:
            # If the user has an unknown role, do not subscribe to any topic
              return

        # Subscribe the token to the appropriate topic
            topic = f'/topics/{topic_name}'
            response = messaging.subscribe_to_topic(self.token, topic, app=FIREBASE_APP)

        # Handle any errors that occur during subscription
            if response.failure_count > 0:
              print(response.errors)
              db_logger.warning(response.errors)
              # errors = [error for error in response.errors]
              # self.deactivate_devices_with_error_results([self.token], errors)


        except IntegrityError:
            # If the token is already in the database, update the last_updated field of the existing token
            existing_token = FCMToken.objects.get(token=self.token)
            existing_token.last_updated = datetime.now()
            existing_token.save(update_fields=['last_updated'])

    def send_message(self,message: messaging.Message,app: FIREBASE_APP,**more_send_message_kwargs) -> Union[Optional[messaging.SendResponse], FirebaseError]:
        message.token = self.token
        try:
            return messaging.SendResponse(
                {"name": messaging.send(message, app=app, **more_send_message_kwargs)},
                None,
            )
        except FirebaseError as e:
           # self.deactivate_devices_with_error_result(self.token, e)
            db_logger.error(traceback.format_exc())
            print(e)
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
from django.db import models

# Create your models here.
