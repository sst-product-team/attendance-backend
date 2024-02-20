# Generated by Django 4.2.8 on 2024-01-10 15:44

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("attendance", "0040_student_personal_mail_problemsolvingpercentage"),
    ]

    operations = [
        migrations.AddField(
            model_name="subjectclass",
            name="class_topic_slug",
            field=models.TextField(default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="subjectclass",
            name="scaler_class_url",
            field=models.URLField(default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="subjectclass",
            name="super_batch_id",
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
    ]
