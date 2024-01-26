from django.db import models
from django.utils.translation import gettext_lazy as _


class User(models.Model):
    full_name = models.CharField(max_length=255, verbose_name=_("Full name"), null=True)
    phone_number = models.CharField(max_length=255, verbose_name=_("Phone number"))
    telegram_id = models.CharField(verbose_name=_("Telegram ID"), unique=True)
    is_active = models.BooleanField(verbose_name=_("Is active"), default=False)
    registered_at = models.DateTimeField(verbose_name=_("Registered at"), auto_now_add=True)

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        return f"{self.phone_number} - {self.telegram_id}"


class VerificationSms(models.Model):
    class Type(models.TextChoices):
        REGISTER = "register", _("Register")
        LOGIN = "login", _("Login")

    user = models.ForeignKey(User, verbose_name=_("User"), on_delete=models.CASCADE, related_name="verification_codes")
    code = models.CharField(max_length=255, verbose_name=_("Code"))
    is_active = models.BooleanField(verbose_name=_("Is active"), default=True)
    expires_in = models.DateTimeField(verbose_name=_("Expires in"))
    hit_count = models.IntegerField(verbose_name=_("Hit count"), default=0)
    type = models.CharField(max_length=255, verbose_name=_("Type"), default=Type.REGISTER, choices=Type.choices)

    class Meta:
        verbose_name = _("Verification SMS")
        verbose_name_plural = _("Verification SMSs")

    def __str__(self):
        return f"{self.user.phone_number} - {self.code}"
