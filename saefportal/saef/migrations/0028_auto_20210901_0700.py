# Generated by Django 3.1.6 on 2021-09-01 07:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('saef', '0027_auto_20210811_0641'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Contact',
        ),
        migrations.DeleteModel(
            name='Settings',
        ),
    ]