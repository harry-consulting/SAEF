# Generated by Django 3.1.6 on 2021-11-11 07:58

import datastores.mixins
from django.db import migrations, models
import fernet_fields.fields


class Migration(migrations.Migration):

    dependencies = [
        ('datastores', '0003_onedrivedatastore'),
    ]

    operations = [
        migrations.CreateModel(
            name='GoogleDriveDatastore',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=100)),
                ('root_path', models.CharField(blank=True, default='', max_length=500)),
                ('token_cache', fernet_fields.fields.EncryptedTextField()),
            ],
            bases=(datastores.mixins.GetConnectionMixin, models.Model),
        ),
    ]
