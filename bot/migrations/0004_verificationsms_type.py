# Generated by Django 5.0 on 2023-12-25 20:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bot", "0003_alter_question_index_alter_question_test_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="verificationsms",
            name="type",
            field=models.CharField(
                choices=[("register", "Register"), ("login", "Login")],
                default="register",
                max_length=255,
                verbose_name="Type",
            ),
        ),
    ]
