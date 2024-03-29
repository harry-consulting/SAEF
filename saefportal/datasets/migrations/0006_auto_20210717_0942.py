# Generated by Django 3.1.6 on 2021-07-17 09:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0005_note'),
    ]

    operations = [
        migrations.AddField(
            model_name='note',
            name='dataset',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='datasets.dataset'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='note',
            name='text',
            field=models.TextField(max_length=2048),
        ),
    ]
