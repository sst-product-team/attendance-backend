# Generated by Django 4.2.7 on 2023-12-08 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0035_alter_classattendance_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectconfiguration',
            name='VERSION_NAME',
            field=models.CharField(default='', max_length=20),
        ),
    ]
