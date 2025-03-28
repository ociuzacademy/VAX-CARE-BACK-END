# Generated by Django 5.1.3 on 2025-03-01 04:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_app', '0004_remove_healthprovider_vaccines'),
    ]

    operations = [
        migrations.AddField(
            model_name='healthprovider',
            name='vaccines',
            field=models.ManyToManyField(related_name='health_providers', to='admin_app.vaccine'),
        ),
    ]
