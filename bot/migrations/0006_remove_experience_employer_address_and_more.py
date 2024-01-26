# Generated by Django 5.0 on 2023-12-26 15:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bot", "0005_alter_jobapplication_birth_date"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="experience",
            name="employer_address",
        ),
        migrations.RemoveField(
            model_name="experience",
            name="employer_name",
        ),
        migrations.AddField(
            model_name="experience",
            name="organization_address",
            field=models.CharField(
                default=1, max_length=255, verbose_name="Organization Address"
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="experience",
            name="organization_name",
            field=models.CharField(
                default=1, max_length=255, verbose_name="Organization name"
            ),
            preserve_default=False,
        ),
    ]