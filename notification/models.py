from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.conf import settings

from account.models import (
    User, 
    UserProfile
)
from base.models import (
    Article,
    Booking,
)

from django.utils import timezone
import datetime
from .tasks import send_scheduled_notification

from myapp.my_utils.string_formater import name_formater
from firebase_admin import messaging


class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True, unique=True, editable=False)
    notification_title = models.CharField(max_length=255)
    notification_body = models.TextField()
    notification_type = models.CharField(max_length=20)
    notification_topic = models.CharField(max_length=25, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=None, null=True, blank=True)

    def __str__(self):
        return self.notification_title


@receiver(post_save, sender=Notification)
def create_notification(sender, instance, created, **kwargs):
    topic = instance.notification_topic if instance.notification_topic is not None else None
    token = instance.user.token_fcm if instance.user.token_fcm is not None else None
    
    if topic:
        message = messaging.Message(
            notification=messaging.Notification(
                title=instance.notification_title,
                body=instance.notification_body
            ),
            topic=topic
        )
    elif token:
        message = messaging.Message(
            notification=messaging.Notification(
                title=instance.notification_title,
                body=instance.notification_body
            ),
            token=token
        )
    else:
        return False
    
    response = messaging.send(message)
    print('Successfully sent message:', response)

    ## Send notification to websocket
    # user_id = instance.user.user_id if instance.user is not None else None
    # async_to_sync(get_channel_layer().group_send)(
    #         'notification',
    #         {
    #             'type': 'push.notification',
    #             'notification_type': instance.notification_type,
    #             'receiver': user_id,
    #             'title': instance.notification_title,
    #             'message': instance.notification_body,
    #         }
    #     )

@receiver(pre_save, sender=User)
def user_verification_status(sender, instance, **kwargs):
    user = sender.objects.filter(user_id=instance.user_id).first()
    if not user:
        return False
    
    ## Check if verification status is not changed 
    if user.verification_status == instance.verification_status:
        return False
    
    ## Check if full name is not set
    if instance.full_name is None:
        return False
    
    title = ""
    message = ""
    name = name_formater(instance.full_name)
    
    if instance.verification_status == "verified":
        title = "Akun Terverifikasi"
        message = f"Hai {name}, akun anda telah terverifikasi."

    elif instance.verification_status == "rejected":
        title = "Akun Ditolak"
        message = f"Hai {name}, akun anda telah ditolak."

    elif instance.verification_status == "pending":
        title = "Akun Menunggu Verifikasi"
        message = f"Hai {name}, akun anda sedang menunggu verifikasi."

    elif instance.verification_status == "suspend":
        title = "Akun Ditangguhkan"
        message = f"Hai {name}, akun anda telah ditangguhkan."

    Notification.objects.create(
        notification_type='User Verification',
        notification_title=title,
        notification_body=message,
        user=instance
    )

@receiver(post_save, sender=UserProfile)
def userprofile_notification(sender, instance, created, **kwargs):
    if created:
        name = name_formater(instance.user.full_name)
        Notification.objects.create(
            notification_type='Registration',
            notification_title="Registration Submitted",
            notification_body=f"Hi {name}, your registration has been submitted and waiting for approval.",
            user=instance.user
        )

@receiver(pre_save, sender=Booking)
def booking_status_notification(sender, instance, **kwargs):
    booking  = sender.objects.filter(booking_id=instance.booking_id).first()
    if not booking:
        return False
    
    if booking.booking_status == instance.booking_status:
        return False


    ## Create notification
    title = ""
    message = ""
    name = name_formater(instance.user.full_name)

    if instance.booking_status == "pending":
        title = "Booking Submitted"
        message = f"Hi {name}, your booking has been submitted and waiting for approval."

    elif instance.booking_status == "active":
        title = "Booking Approved"
        message = f"Hi {name}, your booking has been approved."

        bookingmembers = instance.bookingmember_set.filter().exclude(
            user=instance.user
        ).values('user__user_id', 'user__full_name')
        
        for bookingmember in bookingmembers:
            Notification.objects.create(
                notification_type='Booking',
                notification_title='Anda Ditambahkan ke Booking',
                notification_body=f"Hai {name_formater(bookingmember['user__full_name'])}, anda telah ditambahkan oleh {name} pada {instance.booking_date} di {instance.room.room_name}.",
                user=User.objects.filter(user_id=bookingmember['user__user_id']).first()
            )

        # print(type(instance.booking_date))
        # print(type(instance.bookingtime.end_time))
            
        date = instance.booking_date
        time = instance.bookingtime.end_time
        # print(type(datetime.datetime.strptime(date, '%Y-%m-%d').date()))
        # print(type(datetime.datetime.strptime(time, '%H:%M:%S').time()))

        # date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        # time = datetime.datetime.strptime(time, '%H:%M:%S').time()

        combined = datetime.datetime.combine(date, time)
        # print(combined) 

        # print(f'Datetime: {datetime.datetime.now()}')
        # print(f'Timezone: {timezone.datetime.now()}')
        
        converted_datetime = timezone.make_aware(combined, timezone.get_current_timezone())
        # print(f'Converted: {converted_datetime}')

        notification_dict = [
            {
                'title': 'Pengingat Booking',
                'message': f'Hai {name}, booking anda akan berakhir dalam 10 menit',
                'user_id': instance.user.user_id,
                'booking_id': None,
                'eta': converted_datetime - datetime.timedelta(minutes=10)
            },
            {
                'title': 'Pengingat Booking',
                'message': f'Hai {name}, booking anda akan berakhir dalam 5 menit',
                'user_id': instance.user.user_id,
                'booking_id': None,
                'eta': converted_datetime - datetime.timedelta(minutes=5)
            },
            {
                'title': 'Pengingat Booking',
                'message': f'Hai {name}, booking anda telah berakhir',
                'user_id': instance.user.user_id,
                'booking_id': instance.booking_id,
                'eta': converted_datetime
            }
        ]

        for notification in notification_dict:
            send_scheduled_notification.apply_async(
                (
                    notification['title'],
                    notification['message'],
                    notification['user_id'],
                    notification['booking_id'],
                ),
                eta=notification['eta']
            )

    elif instance.booking_status == "rejected":
        title = "Booking ditolak"
        message = f"Hai {name}, booking anda telah ditolak."

    elif instance.booking_status == "completed":
        title = "Booking Selesai"
        message = f"Hai {name}, booking anda telah selesai."

    elif instance.booking_status == "cancelled":
        title = "Booking Dibatalkan"
        message = f"Hai {name}, booking anda telah dibatalkan."
        
    Notification.objects.create(
        notification_type='Booking',
        notification_title=title,
        notification_body=message,
        user=instance.user
    )
    

@receiver(post_save, sender=Article)
def article_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            notification_type='Article',
            notification_title=instance.article_title,
            notification_body=instance.article_body,
            notification_topic='all_users',
        )



