from datetime import timedelta
from django.conf import settings
from django.db.utils import IntegrityError

from bot.models import *
from bot.utils import generate_code


def create_user(phone_number, telegram_id):
    try:
        user = User.objects.create(
            phone_number=phone_number, telegram_id=telegram_id
        )
        return user
    except IntegrityError:
        raise ValidationError({"message": "user_already_exist"})


def get_user(telegram_id):
    try:
        user = User.objects.get(telegram_id=telegram_id)
        return user
    except User.DoesNotExist:
        raise ValidationError({"message": "user_not_found"})


def create_verification_code(user: User, type: str):
    verify_code = VerificationSms.objects.create(
        user=user, code=generate_code(), type=type,
        expires_in=datetime.now() + timedelta(minutes=int(settings.OTP_EXPIRES_TIME))
    )
    return verify_code


def check_sms_code(user: User, code: str):
    try:
        verify_code = VerificationSms.objects.get(user=user, code=code, is_active=True)
        if verify_code.expires_in > datetime.now():
            verify_code.is_active = False
            verify_code.save()
            if not user.is_active:
                user.is_active = True
                user.save()
            return True
        else:
            verify_code.hit_count += 1
            verify_code.save()
            return False
    except VerificationSms.DoesNotExist:
        return False


def create_job_application(user: User, first_name: str, last_name: str, height: int, weight: int, phone_number: str,
                           email: str, family_status: str, birth_date: str, address: str, requested_position: str,
                           user_photo, user_4x5_photo):
    try:
        job_application = JobApplication.objects.create(
            user=user, first_name=first_name, last_name=last_name, height=height, weight=weight,
            phone_number=phone_number, email=email, family_status=family_status, birth_date=birth_date,
            address=address, requested_position=requested_position, user_photo=user_photo, user_4x5_photo=user_4x5_photo
        )
        return job_application
    except IntegrityError:
        raise ValidationError({"message": "job_application_already_exist"})


def create_computer_skill(application: JobApplication, name, degree):
    try:

        computer_skill = ComputerSkill.objects.create(
            application=application, name=name, degree=degree
        )
        return computer_skill
    except IntegrityError:
        raise ValidationError({"message": "computer_skill_already_exist"})


def create_experience(application: JobApplication, started_date, finished_date, organization_name, organization_address,
                      position, country):
    try:
        experience = Experience.objects.create(
            application=application, started_date=started_date, finished_date=finished_date,
            organization_name=organization_name, organization_address=organization_address, position=position,
            country=country
        )
        return experience
    except IntegrityError:
        raise ValidationError({"message": "experience_already_exist"})


def create_language_skill(application: JobApplication, name, speaking, reading, writing, listening):
    try:
        language_skill = LanguageSkill.objects.create(
            application=application, name=name, speaking=speaking, reading=reading, writing=writing, listening=listening
        )
        return language_skill
    except IntegrityError:
        raise ValidationError({"message": "language_skill_already_exist"})


def create_education(application: JobApplication, started_date, finished_date, title, direction, country):
    try:
        education = Education.objects.create(
            application=application, started_date=started_date, finished_date=finished_date, title=title,
            direction=direction, country=country
        )
        return education
    except IntegrityError:
        raise ValidationError({"message": "education_already_exist"})


def create_applicant_document(application: JobApplication, type, file):
    try:
        applicant_document = ApplicantDoc.objects.create(
            application=application, type=type, file=file
        )
        return applicant_document
    except IntegrityError:
        raise ValidationError({"message": "applicant_document_already_exist"})


def get_tests():
    try:
        tests = Test.objects.all().order_by("index")
        return tests
    except Test.DoesNotExist:
        raise ValidationError({"message": "tests_not_found"})


def get_test(test_id):
    try:
        test = Test.objects.get(id=test_id)
        return test
    except Test.DoesNotExist:
        raise ValidationError({"message": "test_not_found"})


def get_questions(test_id):
    try:
        questions = Question.objects.filter(test_id=test_id).order_by("index")
        return questions
    except Question.DoesNotExist:
        raise ValidationError({"message": "questions_not_found"})


def get_test_answer(answer_id):
    try:
        answer = Answer.objects.get(id=answer_id)
        return answer
    except Answer.DoesNotExist:
        raise ValidationError({"message": "answers_not_found"})


def create_user_test_result(user: User, test: Test, total_ball: int):
    try:
        user_test = UserTest.objects.create(
            user=user, test=test, total_ball=total_ball, is_finished=True,

        )
        return user_test
    except IntegrityError:
        raise ValidationError({"message": "user_test_already_exist"})


def get_ball_range(total_ball, test_id):
    try:
        ball_range = TotalBallRange.objects.filter(from_ball__lte=total_ball, to_ball__gte=total_ball,
                                                   test_id=test_id).first()
        return ball_range
    except TotalBallRange.DoesNotExist:
        raise ValidationError({"message": "ball_range_not_found"})


def get_user_job_application(user: User):
    try:
        job_application = JobApplication.objects.get(user=user)
        return job_application
    except JobApplication.DoesNotExist:
        return None
