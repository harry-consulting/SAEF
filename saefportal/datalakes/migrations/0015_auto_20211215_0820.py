# Generated by Django 3.1.6 on 2021-12-15 08:20

from django.db import migrations
import fernet_fields.fields


class Migration(migrations.Migration):

    dependencies = [
        ('datalakes', '0014_auto_20211215_0815'),
    ]

    operations = [
        migrations.AlterField(
            model_name='azuredatalakedatalake',
            name='connection_string',
            field=fernet_fields.fields.EncryptedCharField(max_length=256),
        ),
    ]