# Generated by Django 5.1.3 on 2025-03-01 07:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_app', '0005_healthprovider_vaccines'),
    ]

    operations = [
        migrations.CreateModel(
            name='TimeSlot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('max_children', models.IntegerField(default=10)),
                ('available_spots', models.IntegerField(default=10)),
                ('health_provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='slots', to='admin_app.healthprovider')),
            ],
        ),
    ]
