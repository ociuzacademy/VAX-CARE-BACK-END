# Generated by Django 5.1.3 on 2025-03-01 04:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('admin_app', '0003_alter_healthprovider_vaccines'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='healthprovider',
            name='vaccines',
        ),
    ]
