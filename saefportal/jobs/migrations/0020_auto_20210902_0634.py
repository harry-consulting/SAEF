# Generated by Django 3.1.6 on 2021-09-02 06:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0019_historicaljob'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicaljob',
            name='description',
            field=models.CharField(blank=True, default='', max_length=1024),
        ),
        migrations.AddField(
            model_name='job',
            name='description',
            field=models.CharField(blank=True, default='', max_length=1024),
        ),
    ]
