# Generated by Django 4.2.7 on 2023-11-09 16:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0007_alter_falseattempt_student_alter_geolocation_student'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classattendancewithgeolocation',
            name='status',
            field=models.CharField(choices=[('proxy', 'Proxy'), ('verifie', 'Verified'), ('standby', 'Standby')], db_index=True, default='standby', max_length=10),
        ),
    ]
