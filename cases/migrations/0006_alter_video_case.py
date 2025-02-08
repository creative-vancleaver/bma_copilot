# Generated by Django 5.1.5 on 2025-02-07 12:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0005_case_date_added_video'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='case',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='videos', to='cases.case'),
        ),
    ]
