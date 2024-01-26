from django.db import models
from django.utils.translation import gettext_lazy as _


class JobApplication(models.Model):
    class Status(models.TextChoices):
        MARRIED = "married", _("Married")
        SINGLE = "single", _("Single")
        DIVORCED = "divorced", _("Divorced")

    user = models.OneToOneField("bot.User", verbose_name=_("User"), on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, verbose_name=_("First name"))
    last_name = models.CharField(max_length=255, verbose_name=_("Last name"))
    height = models.CharField(verbose_name=_("Height"), max_length=10)
    weight = models.CharField(verbose_name=_("Weight"), max_length=10)
    phone_number = models.CharField(max_length=14, verbose_name=_("Phone number"))
    email = models.EmailField(verbose_name=_("Email"))
    family_status = models.CharField(max_length=255, verbose_name=_("Family Status"), choices=Status.choices)
    birth_date = models.CharField(verbose_name=_("Birth date"))
    address = models.CharField(max_length=255, verbose_name=_("Address"))
    requested_position = models.CharField(max_length=255, verbose_name=_("Requested position"))
    user_photo = models.ImageField(verbose_name=_("User Photo"), upload_to="user_photos/")
    user_4x5_photo = models.ImageField(verbose_name=_("User 4x5 Photo"), upload_to="user_4x5_photos/")

    class Meta:
        verbose_name = _("Job application")
        verbose_name_plural = _("Job applications")

    def __str__(self):
        return f"{self.first_name} - {self.last_name}"


