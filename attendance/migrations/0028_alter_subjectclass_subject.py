# Generated by Django 4.2.7 on 2023-11-24 04:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0027_subject_subjectclass_subject'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subjectclass',
            name='subject',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='attendance.subject'),
        ),
    ]