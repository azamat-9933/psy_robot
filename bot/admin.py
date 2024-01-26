from django.contrib import admin
from django.contrib.auth.models import User as DjangoUser, Group
from bot.models import *

admin.site.unregister(Group)
admin.site.unregister(DjangoUser)


@admin.register(VerificationSms)
class VerificationSmsAdmin(admin.ModelAdmin):
    list_display = ("user", "code", "expires_in", "hit_count")

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


class ApplicantDocInline(admin.TabularInline):
    model = ApplicantDoc
    extra = 1


class ComputerSkillInline(admin.TabularInline):
    model = ComputerSkill
    extra = 1


class EducationInline(admin.TabularInline):
    model = Education
    extra = 1


class ExperienceInline(admin.TabularInline):
    model = Experience
    extra = 1


class LanguageSkillInline(admin.TabularInline):
    model = LanguageSkill
    extra = 1


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ("user", "first_name", "last_name", "phone_number", "email",
                    "birth_date", "address")

    list_filter = ("user", "first_name", "last_name", "phone_number", "email")
    search_fields = ("user", "first_name", "last_name", "phone_number", "email")
    inlines = [ApplicantDocInline, ComputerSkillInline, EducationInline,
               ExperienceInline, LanguageSkillInline]


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("telegram_id", "full_name", "phone_number", "is_active", "registered_at")


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ("title", "question_count", "answer_count_in_question", "index")
    inlines = [QuestionInline]


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 1


class QuestionAdmin(admin.ModelAdmin):
    list_display = ("test", "text", "index")
    inlines = [AnswerInline]


admin.site.register(Question, QuestionAdmin)


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("question", "text", "index_format", "ball")


@admin.register(TotalBallRange)
class TotalBallRangeAdmin(admin.ModelAdmin):
    list_display = ("test", "from_ball", "to_ball")


@admin.register(UserTest)
class UserTestAdmin(admin.ModelAdmin):
    list_display = ("user", "test", "is_finished", "total_ball", "finished_at")

    list_filter = ("user", "test", "is_finished")
    search_fields = ("user", "test", "total_ball")
