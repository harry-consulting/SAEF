# Generated by Django 3.1.6 on 2021-07-04 08:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0003_auto_20210704_1008'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='schedule_cron_syntax',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='schedule_end_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='End time'),
        ),
        migrations.AlterField(
            model_name='job',
            name='schedule_parameters',
            field=models.JSONField(blank=True, default=dict, null=True, verbose_name='Parameters'),
        ),
        migrations.AlterField(
            model_name='job',
            name='schedule_start_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Start time'),
        ),
    ]