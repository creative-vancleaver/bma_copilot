# Generated by Django 5.1.5 on 2025-02-06 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cells', '0003_rename_cell_image_cell_image_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cell',
            name='BR_x_in_region',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='cell',
            name='BR_y_in_region',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='cell',
            name='TL_x_in_region',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='cell',
            name='TL_y_in_region',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='cell',
            name='center_x_in_region',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='cell',
            name='center_y_in_region',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='celldetection',
            name='detection_score',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='celldetection',
            name='model_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
