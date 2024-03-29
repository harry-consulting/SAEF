# Generated by Django 3.1.6 on 2021-10-30 09:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('datasets', '0039_delete_azureblobstorageconnection'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='postgresconnection',
            name='connection',
        ),
        migrations.AddField(
            model_name='connection',
            name='datastore_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='connection',
            name='datastore_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
        ),
        migrations.DeleteModel(
            name='AzureConnection',
        ),
        migrations.DeleteModel(
            name='PostgresConnection',
        ),
    ]
