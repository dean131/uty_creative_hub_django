# tasks.py
from celery import shared_task


import notification.models
import account.models
import base.models

@shared_task
def send_scheduled_notification(title, body, user_id, booking_id=None):
    user = account.models.User.objects.filter(user_id=user_id).first()
    notification.models.Notification.objects.create(
        notification_type='Booking',
        notification_title=title,
        notification_body=body,
        user=user
    )

    if booking_id:
        booking = base.models.Booking.objects.filter(booking_id=booking_id).first()
        booking.booking_status = "completed"
        booking.save()
    
    
