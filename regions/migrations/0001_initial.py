# Generated by Django 4.2.19 on 2025-02-10 22:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cases', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Region',
            fields=[
                ('region_id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('time_stamp', models.DateTimeField(blank=True, null=True)),
                ('TL_x_in_frame', models.FloatField(blank=True, null=True)),
                ('TL_y_in_frame', models.FloatField(blank=True, null=True)),
                ('BR_x_in_frame', models.FloatField(blank=True, null=True)),
                ('BR_y_in_frame', models.FloatField(blank=True, null=True)),
                ('group_id', models.IntegerField(blank=True, null=True)),
                ('case', models.ForeignKey(db_column='case_id', on_delete=django.db.models.deletion.CASCADE, related_name='regions', to='cases.case')),
                ('video', models.ForeignKey(blank=True, db_column='video_id', null=True, on_delete=django.db.models.deletion.CASCADE, to='cases.video')),
            ],
            options={
                'db_table': 'region',
            },
        ),
        migrations.CreateModel(
            name='RegionClassification',
            fields=[
                ('region', models.OneToOneField(db_column='region_id', on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='regions.region')),
                ('region_classification_score', models.FloatField(blank=True, null=True)),
                ('is_selected_by_region_classifier', models.BooleanField(default=False)),
                ('region_classifier_id', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'region_classification',
            },
        ),
        migrations.CreateModel(
            name='RegionImage',
            fields=[
                ('region', models.OneToOneField(db_column='region_id', on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='regions.region')),
                ('region_image_path', models.CharField(blank=True, max_length=255, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to=models.CharField(blank=True, max_length=255, null=True))),
            ],
            options={
                'db_table': 'region_image_selected',
            },
        ),
        migrations.AddIndex(
            model_name='region',
            index=models.Index(fields=['case'], name='region_case_id_e30c6b_idx'),
        ),
    ]
