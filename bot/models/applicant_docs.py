from django.db import models
from django.utils.translation import gettext_lazy as _

from bot.models import JobApplication


class ApplicantDoc(models.Model):
    class DocType(models.TextChoices):
        CERTIFICATE = "certificate", _("Certificate")
        DIPLOMA = "diploma", _("Diploma")

    application = models.ForeignKey(JobApplication, verbose_name=_("Application"), on_delete=models.CASCADE,
                                    related_name="docs")
    type = models.CharField(max_length=255, verbose_name=_("Type"), choices=DocType.choices)
    file = models.FileField(upload_to='applicant_docs/', verbose_name=_("File"))

    class Meta:
        verbose_name = _("Applicant doc")
        verbose_name_plural = _("Applicant docs")

    def __str__(self):
        return f"{self.application.id}-{self.type}"

