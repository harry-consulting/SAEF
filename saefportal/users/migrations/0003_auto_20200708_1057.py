# Generated by Django 3.0.3 on 2020-07-08 10:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_userprofile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='firstname',
            field=models.CharField(default='', max_length=32),
        ),
    ]