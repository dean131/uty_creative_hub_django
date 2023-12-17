# tasks.py
from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


import notification.models
import account.models

@shared_task
def send_scheduled_notification(title, body, user_id):
    user = account.models.User.objects.filter(user_id=user_id).first()
    notification.models.Notification.objects.create(
        notification_title=title,
        notification_body=body,
        user=user
    )
    # async_to_sync(get_channel_layer().group_send)(
    #         'notification',
    #         {
    #             'type': 'push.notification',
    #             'receiver': user,
    #             'title': title,
    #             'message': body,
    #         }
    #     )
    
    
