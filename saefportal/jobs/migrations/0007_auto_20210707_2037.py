# Generated by Django 3.1.6 on 2021-07-07 18:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0006_auto_20210707_2025'),
    ]

    operations = [
        migrations.RenameField(
            model_name='notebooktask',
            old_name='notebook_path',
            new_name='notebook_file',
        ),
    ]
