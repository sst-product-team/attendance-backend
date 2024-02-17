# Generated by Django 4.2.8 on 2024-01-11 10:53

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("attendance", "0042_alter_subjectclass_class_topic_slug"),
    ]

    operations = [
        migrations.AlterField(
            model_name="subjectclass",
            name="class_topic_slug",
            field=models.CharField(blank=True, max_length=300),
        ),
        migrations.AlterField(
            model_name="subjectclass",
            name="scaler_class_url",
            field=models.URLField(blank=True, max_length=400),
        ),
    ]
