from django.db import models
from django.utils.translation import gettext_lazy as _

from bot.models import JobApplication


class ComputerSkill(models.Model):
    class Degree(models.TextChoices):
        BEGINNER = "beginner", _("Beginner")
        INTERMEDIATE = "intermediate", _("Intermediate")
        ADVANCED = "advanced", _("Advanced")

    application = models.ForeignKey(JobApplication, verbose_name=_("Application"), on_delete=models.CASCADE,
                                    related_name="computer_skills")
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    degree = models.CharField(max_length=255, verbose_name=_("Degree"), choices=Degree.choices)

    class Meta:
        verbose_name = _("Computer skill")
        verbose_name_plural = _("Computer skills")

    def __str__(self):
        return f"{self.application.id}-{self.name}"
