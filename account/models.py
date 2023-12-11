import uuid
import datetime

from django.utils import timezone
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

from base.models import StudyProgram, Faculty


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            **extra_fields,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        user = self.create_user(
            email,
            password=password,
            **extra_fields,
        )
        user.is_admin = True
        user.is_active = True
        user.verification_status = 'verified'
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    VERIFICATION_STATUS = (
        ('unverified', 'Unverified'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected')
    )

    user_id = models.CharField(max_length=100, primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)

    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    verification_status = models.CharField(max_length=10, default='unverified', choices=VERIFICATION_STATUS)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        'Does the user have a specific permission?'
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        'Does the user have permissions to view the app `app_label`?'
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        'Is the user a member of staff?'
        # Simplest possible answer: All admins are staff
        return self.is_admin
    

class UserProfile(models.Model):
    userprofile_id = models.AutoField(primary_key=True, unique=True)
    student_id_number = models.CharField(max_length=30)
    birth_place = models.CharField(max_length=255, null=True, blank=True)
    birth_date = models.DateField()
    whatsapp_number = models.CharField(max_length=30)
    student_id_card_pic = models.ImageField(upload_to='student_id_card_pics', blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pics', blank=True, null=True)

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    studyprogram = models.ForeignKey(StudyProgram, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.full_name if self.user.full_name else self.userprofile_id


class OTPCode(models.Model):
    code = models.CharField(max_length=4)
    expire = models.DateTimeField()
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.expire = timezone.now() + datetime.timedelta(minutes=5)
        super(OTPCode, self).save(*args, **kwargs)

    def __str__(self):
        return self.code
    



