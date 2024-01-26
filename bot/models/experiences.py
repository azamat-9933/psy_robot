from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from bot.models import JobApplication


class Experience(models.Model):
    application = models.ForeignKey(JobApplication, verbose_name=_("Application"), on_delete=models.CASCADE,
                                    related_name="experiences")
    started_date = models.CharField(verbose_name=_("Start date"), max_length=10)
    finished_date = models.CharField(verbose_name=_("Finish date"), max_length=10)
    organization_name = models.CharField(max_length=255, verbose_name=_("Organization name"))
    organization_address = models.CharField(max_length=255, verbose_name=_("Organization Address"))
    position = models.CharField(max_length=255, verbose_name=_("Position"))
    country = models.CharField(max_length=255, verbose_name=_("Country"))

    class Meta:
        verbose_name = _("Experience")
        verbose_name_plural = _("Experiences")

    def __str__(self):
        return f"{self.application.id}|{self.organization_name} - {self.position}"

    def clean(self):
        if self.started_date >= self.finished_date:
            raise ValidationError(_("Start date must be less than finish date"))