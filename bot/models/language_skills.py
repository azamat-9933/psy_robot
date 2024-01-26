from django.db import models
from django.utils.translation import gettext_lazy as _

from bot.models import JobApplication


class LanguageSkill(models.Model):
    class Degree(models.TextChoices):
        BEGINNER = "beginner", _("Beginner")
        INTERMEDIATE = "intermediate", _("Intermediate")
        ADVANCED = "advanced", _("Advanced")

    application = models.ForeignKey(JobApplication, verbose_name=_("Application"), on_delete=models.CASCADE,
                                    related_name="language_skills")
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    speaking = models.CharField(max_length=255, verbose_name=_("Speaking"), choices=Degree.choices)
    reading = models.CharField(max_length=255, verbose_name=_("Reading"), choices=Degree.choices)
    writing = models.CharField(max_length=255, verbose_name=_("Writing"), choices=Degree.choices)
    listening = models.CharField(max_length=255, verbose_name=_("Listening"), choices=Degree.choices)

    class Meta:
        verbose_name = _("Language skill")
        verbose_name_plural = _("Language skills")

    def __str__(self):
        return f"{self.application.id}-{self.name}"
