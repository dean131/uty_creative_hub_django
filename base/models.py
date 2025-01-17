import uuid
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.translation import gettext as _
from django.utils.timesince import timesince

from django.db import models
from django.conf import settings
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver


class Faculty(models.Model):
    faculty_id = models.AutoField(primary_key=True, unique=True, editable=False)
    faculty_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.faculty_name


class StudyProgram(models.Model):
    studyprogram_id = models.AutoField(primary_key=True, unique=True, editable=False)
    study_program_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)

    def __str__(self):
        return self.study_program_name


class Room(models.Model):
    room_id = models.AutoField(primary_key=True, unique=True, editable=False)
    room_name = models.CharField(max_length=100)
    floor = models.IntegerField()
    room_type = models.CharField(max_length=30)
    room_capacity = models.IntegerField()
    room_description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Rating
    room_rating = models.FloatField(default=0.0)
    total_raters = models.IntegerField(default=0)

    def __str__(self):
        return self.room_name
    

class RoomType(models.Model):
    roomtype_id = models.AutoField(primary_key=True, unique=True, editable=False)
    room_type_name = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.room_type_name
    

class RoomImage(models.Model):
    roomimage_id = models.AutoField(primary_key=True, unique=True, editable=False)
    room_image = models.ImageField(upload_to="room_images")
    created_at = models.DateTimeField(auto_now_add=True)
    
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.room.room_name
    

class RoomFacility(models.Model):
    roomfacility_id = models.AutoField(primary_key=True, unique=True, editable=False)
    facility_name = models.CharField(max_length=255)
    facility_icon = models.ImageField(upload_to="facility_icons")
    created_at = models.DateTimeField(auto_now_add=True)

    room = models.ForeignKey(Room, on_delete=models.CASCADE)

    def __str__(self):
        return self.facility_name


class BookingTime(models.Model):
    bookingtime_id = models.CharField(max_length=2, primary_key=True, unique=True)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return self.start_time.strftime("%H:%M") + " - " + self.end_time.strftime("%H:%M")


class Booking(models.Model):
    class Meta:
        ordering = ["-created_at"]

    BOOKING_STATUS = (
        ("initiated", "Initiated"),
        ("pending", "Pending"),
        ("active", "Active"),
        ("completed", "Completed"),
        ("rejected", "Rejected"),
        ("canceled", "Canceled"),
        ("expired", "Expired"),
    )

    booking_id = models.CharField(max_length=10, primary_key=True, unique=True, editable=False)
    booking_date = models.DateField()
    booking_status = models.CharField(max_length=30, default="pending", choices=BOOKING_STATUS)
    booking_needs = models.TextField(null=True, blank=True)
    cancellation_reason = models.TextField(default="", null=True, blank=True)
    is_rated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    bookingtime = models.ForeignKey(BookingTime, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.room.room_name
    
    def save(self, *args, **kwargs):
        # Generate unique custom booking_id
        if not self.booking_id:
            custom_id = f'UCH-{uuid.uuid4().hex[:6].upper()}'
            while Booking.objects.filter(booking_id=custom_id).exists():
                custom_id = f'UCH-{uuid.uuid4().hex[:6].upper()}'
            self.booking_id = custom_id

        super().save(*args, **kwargs)

    # return True if booking is expired
    @property
    def is_expired(self):
        date = self.booking_date
        time = self.bookingtime.start_time
        aware_date = timezone.make_aware(timezone.datetime.combine(date, time))
        return aware_date <= timezone.now()
    
    def reschedule(self, new_booking_date, new_bookingtime):
        self.booking_date = new_booking_date
        self.bookingtime = new_bookingtime
        self.booking_status = "active"
        self.save()
          

class BookingMember(models.Model):
    bookingmember_id = models.AutoField(primary_key=True, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.full_name 
    

class Rating(models.Model):
    rating_id = models.AutoField(primary_key=True, unique=True, editable=False)
    rating_value = models.FloatField()
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return str(self.rating_id)


class Article(models.Model):
    class Meta:
        ordering = ["-created_at"]
        
    article_id = models.AutoField(primary_key=True, unique=True, editable=False)
    article_type = models.CharField(max_length=30)
    article_title = models.CharField(max_length=100)
    article_body = models.TextField()
    article_link = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.article_title
    
    @property
    def time_since(self):
        return f"{timesince(self.created_at, depth=1)} yang lalu"
    
    @property
    def formated_created_at(self):
        localized_date = timezone.localtime(self.created_at)
        
        components = {
            'hari': date_format(localized_date, 'l'),
            'tanggal': date_format(localized_date, 'd'),
            'bulan': _(date_format(localized_date, 'F')),
            'tahun': date_format(localized_date, 'Y'),
            'waktu': date_format(localized_date, 'H:i')
        }
        
        return "{hari}, {tanggal} {bulan} {tahun} {waktu} WIB".format(**components)


class ArticleImage(models.Model):
    articleimage_id = models.AutoField(primary_key=True, unique=True, editable=False)
    article_image = models.ImageField(upload_to="article_images")
    created_at = models.DateTimeField(auto_now_add=True)
    
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.article.article_title


class Committee(models.Model):
    committee_id = models.AutoField(primary_key=True, unique=True, editable=False)
    committee_name = models.CharField(max_length=255)
    committee_position = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.committee_name


class Banner(models.Model):
    banner_id = models.AutoField(primary_key=True, unique=True, editable=False)
    banner_image = models.ImageField(upload_to="banner_images")
    created_at = models.DateTimeField(auto_now_add=True)


class CeleryTask(models.Model):
    celerytask_id = models.AutoField(primary_key=True, unique=True, editable=False)
    task_id = models.CharField(max_length=100)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)

    def __str__(self):
        return self.task_id


### SIGNALS ###
@receiver(post_save, sender=Booking)
def create_bookingmember(sender, instance, created, **kwargs):
    if created:
        BookingMember.objects.create(
            user=instance.user,
            booking=instance,
        )

@receiver(post_save, sender=Rating)
def update_room_rating(sender, instance, created, **kwargs):
    if created:
        room = instance.booking.room
        total_raters = room.total_raters
        total_rating = room.room_rating * total_raters

        total_rating += instance.rating_value
        total_raters += 1

        room.room_rating = total_rating / total_raters
        room.total_raters = total_raters

        instance.booking.is_rated = True
        instance.booking.save()
        room.save()

@receiver(pre_delete, sender=Rating)
def update_room_rating_delete(sender, instance, **kwargs):
    room = instance.booking.room
    total_raters = room.total_raters
    total_rating = room.room_rating * total_raters

    total_rating -= instance.rating_value
    total_raters -= 1

    if total_raters <= 0:
        room.room_rating = 0
        room.total_raters = 0
    else:
        room.room_rating = total_rating / total_raters
        room.total_raters = total_raters
    room.save()

    