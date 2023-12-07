from django.urls import reverse

from rest_framework.test import APITestCase

from base.models import Booking, Room
from account.models import User



# class TestBookingMember(APITestCase):
#     def setUp(self):
#         self.user = None
#         self.booking = None
#         self.authenticate()
#         self.instance_related_creation()

#     def instance_related_creation(self):
#         booking = Booking.objects.create(

#         )
#         self.booking = booking

#     def authenticate(self):
#         data = {
#             "full_name": "Test",
#             "email": "test@gmail.com",
#             "password": "test1234",
#             "confirm_password": "test1234"
#         }
#         self.client.post(reverse('register'), data)

#         user = User.objects.filter(email='test@gmail.com').first()
#         user.is_active = True
#         user.is_verified = True
#         user.save()

#         self.user = user
        
#         data = {
#             "email": "test@gmail.com",
#             "password": "test1234"
#         }
#         response = self.client.post(reverse('login'), data)
#         self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])

#     def test_create_bookingmember(self):
#         data = {
#             "full_name": "Test",
#             "student_id_number": "1234567890",
#             "studyprogram": "S1 Teknik Informatika",
#             "booking": 1
#         }
#         response = self.client.post(reverse('bookingmember-list'), data)
#         print(response.data)
#         self.assertEqual(response.status_code, 201)