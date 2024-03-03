import json
from django.urls import reverse
from rest_framework.test import APITestCase

from account.models import OTPCode, User
from base.models import StudyProgram, Faculty


class TestRegister(APITestCase):

    def setUp(self):
        faculty = Faculty.objects.create(faculty_name='saintek')
        StudyProgram.objects.create(
            study_program_name="informatika",
            faculty=faculty
        )

    def authenticated(self):
        data = {
            "full_name": "test",
            "email": "test@gmail.com",
            "password": "12345678",
            "confirm_password": "12345678"
        }
        response = self.client.post(reverse('register'), data)

        user = User.objects.filter(email='test@gmail.com').first()
        user.is_active = True
        user.is_verified = True
        user.save()

        data = {
            "email": "test@gmail.com",
            "password": "12345678"
        }
        response = self.client.post(reverse('login'), data)
        access_token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    def test_register(self):
        # RegisterAPIView
        data = {
            "full_name": "test",
            "email": "banjarbanjar23@gmail.com",
            "password": "12345678",
            "confirm_password": "12345678"
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'success': True, 'message': 'OTP Code has been sent to your email'})

        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'success': True, 'message': 'OTP Code has been sent to your email'})

        otpcode = OTPCode.objects.filter(user__email='banjarbanjar23@gmail.com', user__is_active=False).first()

        # ConfirmEmailAPIView
        data = {
            "email": "banjarbanjar23@gmail.com",
            "otp": str(otpcode.code)
        }
        response = self.client.post(reverse('confirm_email'), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'success': True, 'message': 'Email is active'})

        data = {
            "email": "banjarbanjar23@gmail.com",
            "student_id_number" : "5210411101",
            "birth_place" : "german",
            "birth_date" : "2000-01-01",
            "whatsapp_number" : "088888888",
            "study_program" : 1
        }
        response = self.client.post(reverse('userprofile-list'), data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(response.data['message'], 'User profile berhasil dibuat')

        user = User.objects.filter(email='banjarbanjar23@gmail.com').first()
        self.assertEqual(user.is_active, True)
        self.assertEqual(user.is_verified, False)







