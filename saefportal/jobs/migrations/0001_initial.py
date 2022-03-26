# Generated by Django 3.1.6 on 2021-07-02 15:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('time_out', models.IntegerField(default=120)),
                ('retries', models.IntegerField(default=0)),
                ('wait_time_between_retry', models.IntegerField(default=30)),
                ('last_used_parameters', models.JSONField(blank=True, default=dict, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ScheduledJobTrigger',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('schedule_cron_syntax', models.TextField(max_length=512)),
                ('start_time', models.DateTimeField(verbose_name='Start Time')),
                ('end_time', models.DateTimeField(verbose_name='End_Time')),
                ('parameters', models.JSONField(default=dict)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jobs.job')),
            ],
        ),
        migrations.CreateModel(
            name='JobRunHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField(verbose_name='Run Start Time')),
                ('end_time', models.DateTimeField(verbose_name='Run End Time')),
                ('status', models.CharField(max_length=64)),
                ('log_file', models.CharField(max_length=2048)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jobs.job')),
            ],
        ),
        migrations.CreateModel(
            name='JobAlert',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('on_start_email', models.CharField(max_length=500)),
                ('on_success_email', models.CharField(max_length=500)),
                ('on_failure_email', models.CharField(max_length=500)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jobs.job')),
            ],
        ),
    ]