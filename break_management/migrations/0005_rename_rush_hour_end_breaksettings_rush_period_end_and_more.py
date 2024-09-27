# Generated by Django 5.1.1 on 2024-09-27 23:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('break_management', '0004_alter_breakslot_agent_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='breaksettings',
            old_name='rush_hour_end',
            new_name='rush_period_end',
        ),
        migrations.RenameField(
            model_name='breaksettings',
            old_name='rush_hour_start',
            new_name='rush_period_start',
        ),
        migrations.AddField(
            model_name='breaksettings',
            name='reduced_break_slots',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
