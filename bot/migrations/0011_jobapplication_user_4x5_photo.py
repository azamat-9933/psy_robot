# Generated by Django 5.0 on 2024-01-06 22:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bot", "0010_alter_usertest_finished_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="jobapplication",
            name="user_4x5_photo",
            field=models.ImageField(
                default=1, upload_to="user_4x5_photos/", verbose_name="User 4x5 Photo"
            ),
            preserve_default=False,
        ),
    ]
