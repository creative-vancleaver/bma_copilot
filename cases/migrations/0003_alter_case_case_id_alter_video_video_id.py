# Generated by Django 4.2.19 on 2025-02-13 20:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='case_id',
            field=models.CharField(default=None, max_length=255, primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='video',
            name='video_id',
            field=models.CharField(default=None, max_length=255, primary_key=True, serialize=False, unique=True),
        ),
    ]
