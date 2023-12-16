from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from account.models import UserProfile
from base.models import BookingMember
from base.api.serializers.bookingmember_serializers import BookingMemberModelSerializer
from myapp.my_utils.custom_response import CustomResponse


class BookingMemberModelViewSet(ModelViewSet):
    queryset = BookingMember.objects.all()
    serializer_class = BookingMemberModelSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        student_id_number = request.data.get('student_id_number')

        userprofile = UserProfile.objects.filter(
            student_id_number=student_id_number).first()
        
        if not userprofile:
            return CustomResponse.not_found(
                message="Student is not registered"
            )
        
        if userprofile.user.verification_status != 'verified':
            return CustomResponse.bad_request(
                message="Student is not verified"
            )
        
        booking = request.user.booking_set.filter(
            booking_status='initiated').first()
        
        if self.get_queryset().filter(
            user=userprofile.user,
            booking=booking).exists():
            return CustomResponse.bad_request(
                message="Student ID Number already exists"
            )

        request.data.update({
            'booking': booking.booking_id,
            'user': userprofile.user.user_id
        })
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return CustomResponse.created(
                data=serializer.data,
                message="Booking member created successfully",
                headers=headers
            )
        return CustomResponse.serializers_erros(serializer.errors)
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            student_id_number = instance.booking.user.userprofile.student_id_number
            if student_id_number == instance.user.userprofile.student_id_number:
                return CustomResponse.bad_request(
                    message="You can't delete yourself",
                )
            self.perform_destroy(instance)
            return CustomResponse.ok(
                message="Booking member deleted successfully",
            )
        except:
            return CustomResponse.not_found(
                message="Booking member not found",
            )


        
