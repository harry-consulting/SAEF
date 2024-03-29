# Generated by Django 3.1.6 on 2021-07-09 06:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0007_auto_20210707_2037'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='retries',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='job',
            name='time_out',
            field=models.PositiveIntegerField(default=120),
        ),
        migrations.AlterField(
            model_name='job',
            name='wait_time_between_retry',
            field=models.PositiveIntegerField(default=30),
        ),
    ]
