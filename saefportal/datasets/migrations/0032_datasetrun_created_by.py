# Generated by Django 3.1.6 on 2021-09-06 07:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0031_auto_20210904_0623'),
    ]

    operations = [
        migrations.AddField(
            model_name='datasetrun',
            name='created_by',
            field=models.CharField(default='', max_length=100),
        ),
    ]