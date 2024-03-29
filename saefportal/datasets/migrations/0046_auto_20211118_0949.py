# Generated by Django 3.1.6 on 2021-11-18 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0045_auto_20211118_0703'),
    ]

    operations = [
        migrations.AlterField(
            model_name='connection',
            name='type',
            field=models.CharField(choices=[('POSTGRES', 'PostgreSQL'), ('AZURE', 'Azure SQL'), ('ONEDRIVE', 'OneDrive'), ('GOOGLE_DRIVE', 'Google Drive'), ('DROPBOX', 'Dropbox'), ('GOOGLE_CLOUD_STORAGE', 'Google Cloud Storage')], max_length=128),
        ),
    ]
