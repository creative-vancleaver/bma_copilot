# Generated by Django 5.1.5 on 2025-02-07 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cells', '0008_alter_cellclassification_cell'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cellclassification',
            name='model_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
