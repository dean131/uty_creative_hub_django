import uuid

from django.db import models
from django.conf import settings
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils.timesince import timesince


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
        ("canceled", "Canceled")
    )

    booking_id = models.CharField(max_length=10, primary_key=True, unique=True, editable=False)
    booking_date = models.DateField()
    booking_status = models.CharField(max_length=30, default="pending", choices=BOOKING_STATUS)
    booking_needs = models.TextField(null=True, blank=True)
    is_rated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    bookingtime = models.ForeignKey(BookingTime, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.room.room_name
    
    def save(self, *args, **kwargs):
        if not self.booking_id:
            custom_id = f'UCH-{uuid.uuid4().hex[:6].upper()}'
            while Booking.objects.filter(booking_id=custom_id).exists():
                custom_id = f'UCH-{uuid.uuid4().hex[:6].upper()}'
            self.booking_id = custom_id
        super().save(*args, **kwargs)
    

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
        indo_days = {
            'Monday': 'Senin',
            'Tuesday': 'Selasa',
            'Wednesday': 'Rabu',
            'Thursday': 'Kamis',
            'Friday': 'Jumat',
            'Saturday': 'Sabtu',
            'Sunday': 'Minggu'
        }
        indo_month = {
            'January': 'Januari',
            'February': 'Februari',
            'March': 'Maret',
            'April': 'April',
            'May': 'Mei',
            'June': 'Juni',
            'July': 'Juli',
            'August': 'Agustus',
            'September': 'September',
            'October': 'Oktober',
            'November': 'November',
            'December': 'Desember'
        }
        indo_day = indo_days[self.created_at.strftime('%A')]
        indo_month = indo_month[self.created_at.strftime('%B')]
        return self.created_at.strftime(f'{indo_day}, %d {indo_month} %Y %H:%M WIB')


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

    