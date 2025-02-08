# Generated by Django 5.1.5 on 2025-02-07 14:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cells', '0007_alter_celldetection_cell'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cellclassification',
            name='cell',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='classification', to='cells.cell'),
        ),
    ]
