# Generated by Django 4.2.7 on 2023-11-11 10:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0017_alter_classattendancebybsm_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classattendancewithgeolocation',
            name='class_attendance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='attendance.classattendance', unique=True),
        ),
    ]
