# Generated by Django 5.1.1 on 2024-09-27 23:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('break_management', '0005_rename_rush_hour_end_breaksettings_rush_period_end_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='breaksettings',
            old_name='rush_period_end',
            new_name='rush_hour_end',
        ),
        migrations.RenameField(
            model_name='breaksettings',
            old_name='rush_period_start',
            new_name='rush_hour_start',
        ),
        migrations.RemoveField(
            model_name='breaksettings',
            name='reduced_break_slots',
        ),
    ]
