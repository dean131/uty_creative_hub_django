from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

from base.models import StudyProgram


class CustomUserManager(BaseUserManager):
    def create_user(self, email, full_name, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            full_name=full_name,
            **extra_fields,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        user = self.create_user(
            email,
            password=password,
            full_name=full_name,
            **extra_fields,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    user_id = models.CharField(max_length=30, primary_key=True, unique=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(verbose_name="email address", max_length=255, unique=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
    

class UserProfile(models.Model):
    profile_id = models.AutoField(primary_key=True, unique=True)
    student_id_number = models.CharField(max_length=30)
    birth_place = models.CharField(max_length=255)
    birth_date = models.DateField()
    whatsapp_number = models.CharField(max_length=30)
    student_id_card_pic = models.ImageField(upload_to="student_id_card_pics", blank=True, null=True)
    profile_pic = models.ImageField(upload_to="profile_pics", blank=True, null=True)

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    study_program = models.ForeignKey(StudyProgram, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.full_name
