# Generated by Django 3.1.6 on 2021-09-21 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_resourcerequest'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resourcerequest',
            name='message',
            field=models.TextField(blank=True, null=True),
        ),
    ]
