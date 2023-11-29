from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


def send_otp(email_dest, name, otp_code):
    template = render_to_string('account/otp.html', {'name': name, 'otp_code': otp_code})
    email = EmailMessage(
            'Email Verification',
            template,
            settings.EMAIL_HOST_USER,
            [email_dest,],
        )
    email.content_subtype = "html"
    email.send(fail_silently=False)