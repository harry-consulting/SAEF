# Generated by Django 3.0.3 on 2020-08-19 10:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('saef', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobSessionMetaData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('actual_execution_time', models.DurationField()),
                ('expected_execution_time', models.DurationField()),
                ('status_type', models.CharField(choices=[('SUCCEEDED', 'SUCCEEDED'), ('SUCCEEDED_ISSUE', 'SUCCEEDED_ISSUE'), ('FAILED', 'FAILED')], max_length=128)),
                ('job_session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='saef.JobSession')),
            ],
        ),
    ]
