# Generated by Django 3.1.6 on 2021-09-07 09:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0002_settings_show_preview_features'),
        ('users', '0008_auto_20210823_1158'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='settings',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='settings.settings'),
        ),
    ]