# Generated by Django 5.1 on 2025-03-08 09:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_app', '0007_remove_timeslot_max_children'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timeslot',
            name='available_spots',
            field=models.IntegerField(default=15),
        ),
    ]
