# Generated by Django 4.2.7 on 2024-02-11 02:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_user_token_fcm'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='token_fcm',
            field=models.TextField(blank=True, null=True),
        ),
    ]