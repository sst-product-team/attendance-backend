# Generated by Django 4.2.7 on 2023-11-20 21:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0022_alter_classattendancebybsm_marked_by'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectConfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('APP_LATEST_VERSION', models.CharField(max_length=12)),
                ('APK_FILE', models.TextField()),
            ],
        ),
    ]
