# Generated by Django 5.0 on 2023-12-25 21:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bot", "0004_verificationsms_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="jobapplication",
            name="birth_date",
            field=models.CharField(verbose_name="Birth date"),
        ),
    ]
