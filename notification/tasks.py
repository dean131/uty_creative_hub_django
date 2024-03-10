from celery import shared_task


import notification.models
import account.models
import base.models


@shared_task
def create_notification(title, body, user_id, booking_id=None, write=True):
    user = account.models.User.objects.filter(user_id=user_id).first()
    notification.models.Notification.objects.create(
        notification_type='Booking',
        notification_title=title,
        notification_body=body,
        notification_topic=user_id,
        user=user,
        write=write,
    )

    # If booking_id is not None, then update the booking status to "completed"
    if booking_id:
        booking = base.models.Booking.objects.filter(booking_id=booking_id).first()
        booking.booking_status = "completed"
        booking.save()

    return body

@shared_task
def send_scheduled_notification(title, body, user_id, booking_id=None, write=True):
    user = account.models.User.objects.filter(user_id=user_id).first()
    notification.models.Notification.objects.create(
        notification_type='Booking',
        notification_title=title,
        notification_body=body,
        notification_topic=user_id,
        user=user,
        write=write,
    )

    # If booking_id is not None, then update the booking status to "completed"
    if booking_id:
        booking = base.models.Booking.objects.filter(booking_id=booking_id).first()
        booking.booking_status = "completed"
        booking.save()

    return body


@shared_task
def booking_expired_check(booking_id):
    booking = base.models.Booking.objects.filter(booking_id=booking_id).first()
    if booking.is_expired and booking.booking_status == "pending":
        booking.booking_status = "expired"
        booking.save()
        
        return f"\nBOOKING {booking.booking_id} HAS EXPIRED"
    return f"\nFROM TASKS BOOKING EXPIRED CHECK: \n IS_EXPIRED: {booking.is_expired}\n BOOKING_STATUS: {booking.booking_status}"
    
    
