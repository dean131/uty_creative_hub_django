from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from account.models import UserProfile
from base.models import BookingMember
from base.api.serializers.bookingmember_serializers import (
    BookingMemberModelSerializer,
    BookingMemberBookingDetailSerializer
)
from myapp.my_utils.custom_response import CustomResponse


class BookingMemberModelViewSet(ModelViewSet):
    queryset = BookingMember.objects.all()
    serializer_class = BookingMemberModelSerializer
    permission_classes = [IsAuthenticated]

    # def get_serializer_class(self):
    #     if self.action == 'create':
    #         return BookingMemberCreateModelSerializer
    #     return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        student_id_number = request.data.get('student_id_number')

        userprofile = UserProfile.objects.filter(
            student_id_number=student_id_number).first()
        
        if not userprofile:
            return CustomResponse.not_found(
                message="Pengguna tidak ditemukan"
            )
        
        if userprofile.user.verification_status != 'verified':
            return CustomResponse.bad_request(
                message="Pengguna belum terverifikasi"
            )
        
        booking = request.user.booking_set.filter(
            booking_status='initiated').first()
        
        if self.get_queryset().filter(
            user=userprofile.user,
            booking=booking).exists():
            return CustomResponse.bad_request(
                message="NPM sudah terdaftar dalam booking ini"
            )

        request.data.update({
            'booking': booking.booking_id,
            'user': userprofile.user.user_id
        })
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            bookingmember = serializer.save()
            headers = self.get_success_headers(serializer.data)

            serializer = BookingMemberBookingDetailSerializer(bookingmember)
            return CustomResponse.created(
                data=serializer.data,
                message="Booking member berhasil dibuat",
                headers=headers
            )
        return CustomResponse.serializers_erros(serializer.errors)
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            student_id_number = instance.booking.user.userprofile.student_id_number
            if student_id_number == instance.user.userprofile.student_id_number:
                return CustomResponse.bad_request(
                    message="Tidak bisa menghapus diri sendiri dari booking member",
                )
            self.perform_destroy(instance)
            return CustomResponse.ok(
                message="Booking member berhasil dihapus",
            )
        except:
            return CustomResponse.not_found(
                message="Booking member tidak ditemukan",
            )


        
