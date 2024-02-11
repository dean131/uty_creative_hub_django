# Generated by Django 4.2.7 on 2024-02-11 14:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_alter_article_article_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='article_image',
        ),
        migrations.CreateModel(
            name='ArticleImage',
            fields=[
                ('articleimage_id', models.AutoField(editable=False, primary_key=True, serialize=False, unique=True)),
                ('article_image', models.ImageField(upload_to='article_images')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.article')),
            ],
        ),
    ]
