# Generated by Django 5.1.5 on 2025-02-06 18:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cells', '0005_cellclassification_basophil_score_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cellclassification',
            name='blast_and_blast_like_score',
        ),
    ]
