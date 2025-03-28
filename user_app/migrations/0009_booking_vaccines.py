# Generated by Django 5.1.3 on 2025-03-01 10:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_app', '0007_remove_timeslot_max_children'),
        ('user_app', '0008_alter_booking_parent'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='vaccines',
            field=models.ManyToManyField(blank=True, to='admin_app.vaccine'),
        ),
    ]
