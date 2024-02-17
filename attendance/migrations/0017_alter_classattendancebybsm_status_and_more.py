# Generated by Django 4.2.7 on 2023-11-11 10:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0016_alter_classattendancebybsm_class_attendance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classattendancebybsm',
            name='status',
            field=models.CharField(choices=[('proxy', 'Proxy'), ('present', 'Present'), ('absent', 'Absent')], default='present', max_length=10),
        ),
        migrations.AlterUniqueTogether(
            name='classattendance',
            unique_together={('student', 'subject')},
        ),
    ]
