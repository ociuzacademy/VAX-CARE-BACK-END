# Generated by Django 5.1.3 on 2025-03-01 09:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_app', '0007_remove_timeslot_max_children'),
        ('user_app', '0005_booking_max_children'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='vaccine',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='admin_app.vaccine'),
            preserve_default=False,
        ),
    ]
