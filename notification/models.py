import datetime

from django.utils import timezone
from django.db import models
from django.db.models.signals import post_save, pre_save, pre_delete
from django.dispatch import receiver
from django.conf import settings

from account.models import (
    User, 
    UserProfile,
)
from base.models import (
    Article,
    Booking,
    CeleryTask,
)

from .tasks import (
    send_scheduled_notification,
    booking_expired_check,

)

from firebase_admin import messaging

from celery.result import AsyncResult


class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True, unique=True, editable=False)
    notification_title = models.CharField(max_length=255)
    notification_body = models.TextField()
    notification_type = models.CharField(max_length=50)
    notification_topic = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    write = models.BooleanField(default=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=None, null=True, blank=True)

    def __str__(self):
        return self.notification_title
    
    def save(self, *args, **kwargs):
        if not self.notification_id:
            message = messaging.Message(
                data={
                    'title': self.notification_title,
                    'body': self.notification_body,
                },
                topic=self.notification_topic,
                android=messaging.AndroidConfig(
                    priority='high',
                )
            )
            messaging.send(message)
        
        # if self.write equals to False, then don't save the notification
        if self.write:
            super().save(*args, **kwargs)
        else:
            return False


# @receiver(post_save, sender=Notification)
# def notification_created_send_notification(sender, instance, created, **kwargs):
#     if created:
#         message = messaging.Message(
#             data={
#                 'title': instance.notification_title,
#                 'body': instance.notification_body,
#             },
#             topic=instance.notification_topic,
#             android=messaging.AndroidConfig(
#                 priority='high',
#             )
#         )
    
#     response = messaging.send(message)
#     print('NOTIFICATION SENT SUCCESSFULLY: ', response)

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
    
    if instance.verification_status == "verified":
        title = "Akun Terverifikasi"
        message = f"Hai {instance.first_name}, akun anda telah terverifikasi."

    elif instance.verification_status == "rejected":
        title = "Akun Ditolak"
        message = f"Hai {instance.first_name}, akun anda telah ditolak."

    elif instance.verification_status == "pending":
        title = "Akun Menunggu Verifikasi"
        message = f"Hai {instance.first_name}, akun anda sedang menunggu verifikasi."

    elif instance.verification_status == "suspend":
        title = "Akun Ditangguhkan"
        message = f"Hai {instance.first_name}, akun anda telah ditangguhkan."

    else:
        title = "Status Akun Tidak Diketahui"
        message = f"Hai {instance.first_name}, status akun anda tidak diketahui."

    Notification.objects.create(
        notification_type='Vefifikasi Akun',
        notification_title=title,
        notification_body=message,
        notification_topic=instance.user_id,
        user=instance
    )

@receiver(post_save, sender=UserProfile)
def userprofile_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            notification_type='Registrasi Akun',
            notification_title="Registrasi Akun",
            notification_body=f"Hai {instance.user.first_name}, selamat datang di aplikasi kami. Silahkan lengkapi data diri anda.",
            notification_topic=instance.user.user_id,
            user=instance.user
        )

@receiver(pre_save, sender=Booking)
def booking_status_notification(sender, instance, **kwargs):
    booking  = sender.objects.filter(booking_id=instance.booking_id).first()
    if not booking:
        return False
    
    # Check if booking status is not changed
    if booking.booking_status == instance.booking_status:
        return False
    
    # delete all related celery tasks if booking status is changed
    celerytasks = CeleryTask.objects.filter(booking=instance)
    if celerytasks.exists():
        celerytasks.delete()
    
    ## Create notification
    title = ""
    message = ""

    if instance.booking_status == "pending":
        title = "Booking Diajukan"
        message = f"Hai {instance.user.first_name}, booking anda dengan ID Reservasi #{instance.booking_id} telah diajukan"
        
        # Combine date and time
        combined_start_time = datetime.datetime.combine(
            instance.booking_date, 
            instance.bookingtime.start_time
        )

        # Make combined date and time aware
        aware_start_date_time = timezone.make_aware(
            combined_start_time, 
            timezone.get_current_timezone()
        )
        
        task = booking_expired_check.apply_async(
            (instance.booking_id,),
            eta=aware_start_date_time
        )

        print(f"\nMENAMBAH TASK (BOOKING EXPIRED CHECK): {task.id}")

    elif instance.booking_status == "active":
        title = "Booking Disetujui"
        message = f"Hai {instance.user.first_name}, booking anda dengan ID Reservasi #{instance.booking_id} telah disetujui"
   
        # Combine date and time
        combined_start_time = datetime.datetime.combine(
            instance.booking_date, 
            instance.bookingtime.start_time
        )
        combined_end_time = datetime.datetime.combine(
            instance.booking_date, 
            instance.bookingtime.end_time
        )
        
        # Make combined date and time aware
        aware_start_date_time = timezone.make_aware(
            combined_start_time, 
            timezone.get_current_timezone()
        )
        aware_end_date_time = timezone.make_aware(
            combined_end_time, 
            timezone.get_current_timezone()
        )

        notification_dict = [
            {
                'title': 'Pengingat Booking',
                'message': f'Hai {instance.user.first_name}, booking anda dengan ID Reservasi #{instance.booking_id} akan dimulai sebentar lagi',
                'booking_id': None,
                'eta': aware_start_date_time - datetime.timedelta(minutes=10),
                'write': False
            },
            {
                'title': 'Pengingat Booking',
                'message': f'Hai {instance.user.first_name}, booking anda dengan ID Reservasi #{instance.booking_id} telah dimulai',
                'booking_id': None,
                'eta': aware_start_date_time,
                'write': False
            },
            {
                'title': 'Pengingat Booking',
                'message': f'Hai {instance.user.first_name}, booking anda dengan ID Reservasi #{instance.booking_id} akan berakhir dalam 10 menit',
                'booking_id': None,
                'eta': aware_end_date_time - datetime.timedelta(minutes=10),
                'write': False
            },
            {
                'title': 'Pengingat Booking',
                'message': f'Hai {instance.user.first_name}, booking anda dengan ID Reservasi #{instance.booking_id} akan berakhir dalam 5 menit',
                'booking_id': None,
                'eta': aware_end_date_time - datetime.timedelta(minutes=5),
                'write': False
            },
            {
                'title': 'Pengingat Booking',
                'message': f'Hai {instance.user.first_name}, booking anda dengan ID Reservasi #{instance.booking_id} telah berakhir',
                'booking_id': instance.booking_id,
                'eta': aware_end_date_time,
                'write': False
            }
        ]
        
        bookingmembers = instance.bookingmember_set.filter()

        for bookingmember in bookingmembers:
            for notification in notification_dict:
                task = send_scheduled_notification.apply_async(
                    (
                        notification['title'],
                        notification['message'],
                        bookingmember.user.user_id,
                        notification['booking_id'],
                        notification['write'],
                    ),
                    eta=notification['eta']
                )
                CeleryTask.objects.create(
                    task_id=task.id,
                    booking=instance
                )
                print(f"MENAMBAH TASK (NOTIFICATION) untuk booking id {instance.booking_id}: {task.id}")

        for bookingmember in bookingmembers.exclude(user=instance.user):
            Notification.objects.create(
                notification_type='Booking',
                notification_title='Anda Ditambahkan ke Booking',
                notification_body=f"Hai {bookingmember.user.first_name}, anda telah ditambahkan oleh {instance.user.first_name} pada {instance.booking_date} di {instance.room.room_name}.",
                notification_topic=bookingmember.user.user_id,
                user=bookingmember.user
            )
            

    elif instance.booking_status == "rejected":
        title = "Booking Ditolak"
        message = f"Hai {instance.user.first_name}, booking anda dengan ID Reservasi #{instance.booking_id} telah ditolak."

    elif instance.booking_status == "completed":
        title = "Booking Selesai"
        message = f"Hai {instance.user.first_name}, booking anda dengan ID Reservasi #{instance.booking_id} telah selesai."

    elif instance.booking_status == "canceled":
        title = "Booking Dibatalkan"
        message = f"Hai {instance.user.first_name}, booking anda dengan ID Reservasi #{instance.booking_id} telah dibatalkan."
        
    Notification.objects.create(
        notification_type='Booking',
        notification_title=title,
        notification_body=message,
        notification_topic=instance.user.user_id,
        user=instance.user
    )


# if celery task deleted, then revoke the task
@receiver(pre_delete, sender=CeleryTask)
def delete_celery_task(sender, instance, **kwargs):
    task = AsyncResult(instance.task_id)
    task.revoke()


# if booking deleted, then delete all related celery tasks
@receiver(pre_delete, sender=Booking)
def delete_celery_tasks_for_booking_reminder(sender, instance, **kwargs):
    celerytasks = CeleryTask.objects.filter(booking=instance)
    if celerytasks.exists():
        for celerytask in celerytasks:
            task = AsyncResult(celerytask.task_id)
            task.revoke()
        celerytasks.delete()
    

@receiver(post_save, sender=Article)
def article_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            notification_type='Article',
            notification_title=instance.article_title,
            notification_body=instance.article_body,
            notification_topic='all_users',
        )




