# Generated by Django 5.0 on 2023-12-27 14:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bot", "0006_remove_experience_employer_address_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="jobapplication",
            name="height",
            field=models.CharField(max_length=10, verbose_name="Height"),
        ),
        migrations.AlterField(
            model_name="jobapplication",
            name="weight",
            field=models.CharField(max_length=10, verbose_name="Weight"),
        ),
    ]
