# Generated by Django 3.1.6 on 2021-11-21 07:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datalakes', '0008_azureblobstoragedatalake'),
    ]

    operations = [
        migrations.AddField(
            model_name='azureblobstoragedatalake',
            name='container_name',
            field=models.CharField(default='test', max_length=200),
            preserve_default=False,
        ),
    ]
