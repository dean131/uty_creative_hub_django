# Generated by Django 4.2.7 on 2024-02-29 14:04

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('user_id', models.CharField(default=uuid.uuid4, editable=False, max_length=100, primary_key=True, serialize=False, unique=True)),
                ('full_name', models.CharField(blank=True, max_length=255, null=True)),
                ('email', models.EmailField(max_length=255, unique=True, verbose_name='email address')),
                ('is_active', models.BooleanField(default=False)),
                ('is_admin', models.BooleanField(default=False)),
                ('verification_status', models.CharField(choices=[('unverified', 'Unverified'), ('verified', 'Verified'), ('rejected', 'Rejected'), ('suspend', 'Suspend')], default='unverified', max_length=10)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OTPCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=4)),
                ('expire', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('userprofile_id', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('student_id_number', models.CharField(max_length=30, unique=True)),
                ('birth_place', models.CharField(blank=True, max_length=255, null=True)),
                ('birth_date', models.DateField()),
                ('whatsapp_number', models.CharField(max_length=30)),
                ('student_id_card_pic', models.ImageField(blank=True, null=True, upload_to='student_id_card_pics')),
                ('profile_pic', models.ImageField(blank=True, null=True, upload_to='profile_pics')),
            ],
        ),
    ]
