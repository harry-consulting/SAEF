# Generated by Django 3.1.6 on 2021-09-07 13:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0002_settings_show_preview_features'),
        ('users', '0009_user_settings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='settings',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='settings.settings'),
        ),
    ]
