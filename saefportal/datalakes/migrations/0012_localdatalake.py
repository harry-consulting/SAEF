# Generated by Django 3.1.6 on 2021-11-28 08:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datalakes', '0011_amazons3datalake'),
    ]

    operations = [
        migrations.CreateModel(
            name='LocalDatalake',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('root_path', models.CharField(blank=True, default='', max_length=500)),
            ],
        ),
    ]
