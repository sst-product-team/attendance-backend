# Generated by Django 4.2.7 on 2023-11-09 17:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0008_alter_classattendancewithgeolocation_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='subjectclass',
            old_name='end_time',
            new_name='attendance_end_time',
        ),
        migrations.RenameField(
            model_name='subjectclass',
            old_name='start_time',
            new_name='attendance_start_time',
        ),
    ]
