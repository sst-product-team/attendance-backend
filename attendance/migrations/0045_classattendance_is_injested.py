# Generated by Django 4.2.8 on 2024-01-16 08:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("attendance", "0044_alter_subjectclass_super_batch_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="classattendance",
            name="is_injested",
            field=models.BooleanField(default=False),
        ),
    ]
