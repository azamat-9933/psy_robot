# Generated by Django 5.0 on 2023-12-24 00:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bot", "0002_question_test_answer_question_test_totalballrange_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="question",
            name="index",
            field=models.IntegerField(unique=True, verbose_name="Index"),
        ),
        migrations.AlterField(
            model_name="question",
            name="test",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="questions",
                to="bot.test",
                verbose_name="Test",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="telegram_id",
            field=models.CharField(unique=True, verbose_name="Telegram ID"),
        ),
        migrations.AlterField(
            model_name="usertest",
            name="finished_at",
            field=models.DateTimeField(verbose_name="Finished at"),
        ),
    ]
