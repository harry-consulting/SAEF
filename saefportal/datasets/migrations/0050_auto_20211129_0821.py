# Generated by Django 3.1.6 on 2021-11-29 08:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0049_auto_20211127_0826'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataset',
            name='connection',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='datasets', to='datasets.connection'),
        ),
    ]
