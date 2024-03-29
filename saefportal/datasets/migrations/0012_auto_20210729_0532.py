# Generated by Django 3.1.6 on 2021-07-29 05:32

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0011_dataset_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='connection',
            name='key',
            field=models.CharField(default=uuid.uuid4, max_length=128, unique=True),
        ),
        migrations.AlterField(
            model_name='dataset',
            name='key',
            field=models.CharField(default=uuid.uuid4, max_length=128, unique=True),
        ),
    ]
