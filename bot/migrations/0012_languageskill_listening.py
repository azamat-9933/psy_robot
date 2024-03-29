# Generated by Django 5.0 on 2024-01-06 23:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bot", "0011_jobapplication_user_4x5_photo"),
    ]

    operations = [
        migrations.AddField(
            model_name="languageskill",
            name="listening",
            field=models.CharField(
                choices=[
                    ("beginner", "Beginner"),
                    ("intermediate", "Intermediate"),
                    ("advanced", "Advanced"),
                ],
                default=1,
                max_length=255,
                verbose_name="Listening",
            ),
            preserve_default=False,
        ),
    ]
