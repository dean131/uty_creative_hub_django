from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.conf import settings

from account.models import User, UserProfile
from base.models import (
    Article,
    Booking,
)

from notification.tasks import send_scheduled_notification
import datetime


def name_formater(full_name):
    full_name = full_name.split(' ')
    return full_name[1] if (len(full_name[0]) < 3 and len(full_name) > 1) else full_name[0]


class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True, unique=True, editable=False)
    notification_title = models.CharField(max_length=255)
    notification_body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=None, null=True, blank=True)

    def __str__(self):
        return self.notification_title


@receiver(post_save, sender=Notification)
def create_notification(sender, instance, created, **kwargs):
    user_id = instance.user.user_id if instance.user is not None else None
    async_to_sync(get_channel_layer().group_send)(
            'notification',
            {
                'type': 'push.notification',
                'receiver': user_id,
                'title': instance.notification_title,
                'message': instance.notification_body,
            }
        )

@receiver(pre_save, sender=User)
def send_notification(sender, instance, **kwargs):
    user = sender.objects.filter(user_id=instance.user_id).first()
    if not user:
        return False
    
    if user.verification_status == instance.verification_status:
        return False
    
    if instance.full_name is None:
        return False
    
    title = ""
    message = ""
    name = name_formater(instance.full_name)
    
    if instance.verification_status == "verified":
        title = "Account Verified"
        message = f"Hi {name}, your account has been verified."

    elif instance.verification_status == "rejected":
        title = "Account Rejected"
        message = f"Hi {name}, your account has been rejected."

    Notification.objects.create(
        notification_title=title,
        notification_body=message,
        user=instance
    )

@receiver(post_save, sender=UserProfile)
def userprofile_notification(sender, instance, created, **kwargs):
    if created:
        name = name_formater(instance.user.full_name)
        Notification.objects.create(
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
                notification_title='Added to Booking',
                notification_body=f"Hi {name_formater(bookingmember['user__full_name'])}, you have been added to a booking by {name} on {instance.booking_date} in {instance.room.room_name}.",
                user=User.objects.filter(user_id=bookingmember['user__user_id']).first()
            )

        send_scheduled_notification.apply_async(
            ('testttt', 'testtt', 'testttt'),
            countdown=5
        )

    elif instance.booking_status == "rejected":
        title = "Booking Rejected"
        message = f"Hi {name}, your booking has been rejected."

    elif instance.booking_status == "done":
        title = "Booking Done"
        message = f"Hi {name}, your booking has been done."
        
    Notification.objects.create(
        notification_title=title,
        notification_body=message,
        user=instance.user
    )

@receiver(post_save, sender=Article)
def article_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            notification_title=instance.article_title,
            notification_body=instance.article_body,
        )



