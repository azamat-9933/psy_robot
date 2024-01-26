from datetime import datetime
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from bot.models import User


class Test(models.Model):
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    question_count = models.IntegerField(verbose_name=_("Question count"))
    answer_count_in_question = models.IntegerField(verbose_name=_("Answer count in question"))
    index = models.IntegerField(verbose_name=_("Index"))

    class Meta:
        verbose_name = _("Test")
        verbose_name_plural = _("Tests")

    def __str__(self):
        return self.title

    def clean(self):
        if self.index < 0:
            raise ValidationError(_("Index must be greater than 0"))


class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, verbose_name=_("Test"), related_name="questions")
    text = models.TextField(verbose_name=_("Text"))
    index = models.IntegerField(verbose_name=_("Index"), unique=True)

    class Meta:
        verbose_name = _("Question")
        verbose_name_plural = _("Questions")

    def __str__(self):
        return self.text

    def clean(self):
        if self.index < 0:
            raise ValidationError(_("Index must be greater than 0"))
        #
        # if self.test.question_count <= Question.objects.count() + 1:
        #     raise ValidationError(_("question_count must be equal question count in test"))


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name=_("Question"),
                                 related_name="answers")
    text = models.TextField(verbose_name=_("Text"))
    index_format = models.IntegerField(verbose_name=_("Index format"))
    ball = models.IntegerField(verbose_name=_("Ball"))

    class Meta:
        verbose_name = _("Answer")
        verbose_name_plural = _("Answers")

    def __str__(self):
        return f"ID: {self.id}"


class TotalBallRange(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, verbose_name=_("Test"))
    from_ball = models.IntegerField(verbose_name=_("From ball"))
    to_ball = models.IntegerField(verbose_name=_("To ball"))
    description = models.TextField(verbose_name=_("Description"))

    class Meta:
        verbose_name = _("Total ball range")
        verbose_name_plural = _("Total ball ranges")

    def __str__(self):
        return f"From: {self.from_ball} To: {self.to_ball}"

    def clean(self):
        if self.from_ball > self.to_ball:
            raise ValidationError(_("From ball must be less than To ball"))


class UserTest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("User"), related_name="user_tests")
    test = models.ForeignKey(Test, on_delete=models.CASCADE, verbose_name=_("Test"), related_name="user_tests")
    is_finished = models.BooleanField(verbose_name=_("Is finished"), default=False)
    total_ball = models.IntegerField(verbose_name=_("Total ball"))
    finished_at = models.DateTimeField(verbose_name=_("Finished at"), auto_now_add=True)

    class Meta:
        verbose_name = _("User test")
        verbose_name_plural = _("User tests")

    def __str__(self):
        return f"User: {self.user.id} Test: {self.test.id}"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.is_finished:
            self.finished_at = datetime.now()

        super().save(force_insert, force_update, using, update_fields)
