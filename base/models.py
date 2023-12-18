from django.db import models
from django.conf import settings
from django.db.models.signals import post_save, post_delete
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
    ROOM_TYPE = (
        ("meeting_room", "Meeting Room"),
    )

    room_id = models.AutoField(primary_key=True, unique=True, editable=False)
    room_name = models.CharField(max_length=100)
    floor = models.IntegerField()
    room_type = models.CharField(max_length=30, choices=ROOM_TYPE)
    room_capacity = models.IntegerField()
    room_description = models.TextField(null=True, blank=True)
    room_rating = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.room_name
    
    def total_raters(self):
        return self.rating_set.count()
    

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
    

class Rating(models.Model):
    rating_id = models.AutoField(primary_key=True, unique=True, editable=False)
    rating_value = models.FloatField()
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.room.room_name


class BookingTime(models.Model):
    bookingtime_id = models.CharField(max_length=2, primary_key=True, unique=True)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return self.start_time.strftime("%H:%M") + " - " + self.end_time.strftime("%H:%M")


class Booking(models.Model):
    BOOKING_STATUS = (
        ("initiated", "Initiated"),
        ("pending", "Pending"),
        ("active", "Active"),
        ("done", "Done"),
        ("rejected", "Rejected"),
    )

    booking_id = models.AutoField(primary_key=True, unique=True, editable=False)
    booking_date = models.DateField()
    booking_status = models.CharField(max_length=30, default="pending", choices=BOOKING_STATUS)
    booking_needs = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    bookingtime = models.ForeignKey(BookingTime, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.room.room_name
    

class BookingMember(models.Model):
    bookingmember_id = models.AutoField(primary_key=True, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.full_name 


class Article(models.Model):
    article_id = models.AutoField(primary_key=True, unique=True, editable=False)
    article_title = models.CharField(max_length=255)
    article_body = models.TextField()
    article_image = models.ImageField(upload_to="article_images", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.article_title
    

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
        room = instance.room
        ratings = Rating.objects.filter(room=room)
        total_rating = 0.0
        for rating in ratings:
            total_rating += rating.rating_value
        room.room_rating = total_rating / ratings.count()
        room.save()

@receiver(post_delete, sender=Rating)
def update_room_rating_delete(sender, instance, **kwargs):
    room = instance.room
    ratings = room.rating_set.filter()
    if not ratings:
        room.room_rating = 0.0
        room.save()
    else:
        total_rating = 0.0
        for rating in ratings:
            total_rating += rating.rating_value
        room.room_rating = total_rating / ratings.count()
        room.save()