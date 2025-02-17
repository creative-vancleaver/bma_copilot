# Generated by Django 4.2.19 on 2025-02-11 01:38

from django.db import migrations, models
import django.db.models.deletion
import users.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('regions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cell',
            fields=[
                ('cell_id', models.CharField(default=None, max_length=255, primary_key=True, serialize=False, unique=True)),
                ('cell_image_path', models.CharField(blank=True, max_length=255, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to=models.CharField(blank=True, max_length=255, null=True))),
                ('center_x_in_region', models.FloatField(blank=True, null=True)),
                ('center_y_in_region', models.FloatField(blank=True, null=True)),
                ('TL_x_in_region', models.FloatField(blank=True, null=True)),
                ('TL_y_in_region', models.FloatField(blank=True, null=True)),
                ('BR_x_in_region', models.FloatField(blank=True, null=True)),
                ('BR_y_in_region', models.FloatField(blank=True, null=True)),
                ('region', models.ForeignKey(db_column='region_id', on_delete=django.db.models.deletion.CASCADE, to='regions.region')),
            ],
            options={
                'db_table': 'cells',
            },
        ),
        migrations.CreateModel(
            name='CellDetection',
            fields=[
                ('cell', models.OneToOneField(db_column='cell_id', on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='cells.cell')),
                ('cell_detection_score', models.FloatField(blank=True, null=True)),
                ('model_id', models.CharField(blank=True, db_column='cell_detection_model_id', max_length=100, null=True)),
                ('is_user_added', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'cell_detection',
            },
        ),
        migrations.CreateModel(
            name='CellClassification',
            fields=[
                ('cell', models.OneToOneField(db_column='cell_id', on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='cells.cell')),
                ('ai_cell_class', models.CharField(blank=True, max_length=250, null=True)),
                ('user_cell_class', models.CharField(blank=True, max_length=250, null=True)),
                ('myelocytes_score', models.FloatField(blank=True, null=True)),
                ('metamyelocytes_score', models.FloatField(blank=True, null=True)),
                ('monocytes_score', models.FloatField(blank=True, null=True)),
                ('eosinophils_score', models.FloatField(blank=True, null=True)),
                ('erythroid_precursors_score', models.FloatField(blank=True, null=True)),
                ('lymphocytes_score', models.FloatField(blank=True, null=True)),
                ('plasma_cells_score', models.FloatField(blank=True, null=True)),
                ('skippocyte_score', models.FloatField(blank=True, null=True)),
                ('blasts_and_blast_equivalents_score', models.FloatField(blank=True, null=True)),
                ('neutrophils_bands_score', models.FloatField(blank=True, null=True)),
                ('cell_classification_model_id', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'cell_classification',
                'indexes': [models.Index(fields=['cell'], name='cell_classi_cell_id_dfb6d9_idx')],
            },
        ),
        migrations.AddIndex(
            model_name='cell',
            index=models.Index(fields=['region'], name='cells_region__44d17a_idx'),
        ),
    ]
