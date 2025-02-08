# Generated by Django 5.1.5 on 2025-02-07 14:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_case_user_alter_cell_region_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cellclassification',
            name='cell',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='core_classification', to='core.cell'),
        ),
    ]
