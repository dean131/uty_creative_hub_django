# Generated by Django 4.2.7 on 2024-02-11 04:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0007_fcmtokens'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='token_fcm',
        ),
    ]