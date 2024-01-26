from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from bot.models import JobApplication


class Education(models.Model):
    application = models.ForeignKey(JobApplication, verbose_name=_("Application"), on_delete=models.CASCADE,
                                    related_name="educations")
    started_date = models.CharField(verbose_name=_("Start date"), max_length=10)
    finished_date = models.CharField(verbose_name=_("Finish date"), max_length=10)
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    direction = models.CharField(max_length=255, verbose_name=_("Direction"), null=True)
    country = models.CharField(max_length=255, verbose_name=_("Country"))

    class Meta:
        verbose_name = _("Education")
        verbose_name_plural = _("Educations")

    def __str__(self):
        return f"{self.title} - {self.direction}"

    def clean(self):
        if self.started_date >= self.finished_date:
            raise ValidationError(_("Start date must be less than finish date"))
