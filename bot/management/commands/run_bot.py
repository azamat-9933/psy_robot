import sentry_sdk
from telebot import TeleBot
from telebot.types import Message, ReplyKeyboardRemove
from django.core.management.base import BaseCommand
from config.settings import config, BASE_DIR
from bot.utils import telegram_pusher, convert_text_to_pdf, email_sender, document_pusher
from bot.keyboards import default, inline
from bot.crud import *
from bot.templates.about_job_application import ABOUT_APPLICATION_MESSAGE, ABOUT_TEST_MESSAGE
from bot.states import *
from bot.templates.generate_html import generate_html

bot = TeleBot(config["BOT_TOKEN"])


@bot.message_handler(commands=["start"])
def start(message: Message) -> None:
    bot.send_message(chat_id=message.chat.id, text="Botdan ruyhatdan otishingiz uchun telefon raqamingizni yuboring\n"
                                                   "Login qilish uchun /login buyrug'ini bering",
                     reply_markup=default.get_contact_phone())


@bot.message_handler(content_types=["contact"])
def register(message: Message):
    telegram_id = message.from_user.id

    try:
        user = create_user(phone_number=message.contact.phone_number, telegram_id=telegram_id)
        verify_code = create_verification_code(user=user, type=VerificationSms.Type.REGISTER)
        telegram_pusher(user=user, code=verify_code.code, expires_in=verify_code.expires_in)
        bot.send_message(chat_id=message.chat.id, text="Telefon raqamingizga tasdiqlash kodi yuborildi.\n"
                                                       "Kodni kiritib accountingizni faollashtiring.")

    except ValidationError:

        bot.send_message(chat_id=message.chat.id, text="Siz allaqachon ruyhatdan utgansiz.\n"
                                                       "Boshqa nomer orqali ruyhatdan uting yoki /login buyrug'i orqali "
                                                       "kirishga urinib ko'ring.")
    except Exception as e:
        sentry_sdk.capture_exception(e)
        bot.send_message(chat_id=message.chat.id, text="Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")


@bot.message_handler(commands=["login"])
def login(message: Message):
    try:
        user = get_user(telegram_id=message.from_user.id)
        verify_code = create_verification_code(user=user, type=VerificationSms.Type.LOGIN)
        telegram_pusher(user=user, code=verify_code.code, expires_in=verify_code.expires_in)
        bot.send_message(chat_id=message.chat.id, text="Telefon raqamingizga tasdiqlash kodi yuborildi.\n",
                         reply_markup=ReplyKeyboardRemove())
    except ValidationError:
        bot.send_message(chat_id=message.chat.id, text="Siz ruyhatdan utmagansiz.\n"
                                                       "Iltimos, avval ruyhatdan uting.")

    except Exception as e:
        sentry_sdk.capture_exception(e)
        bot.send_message(chat_id=message.chat.id, text="Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")


@bot.message_handler(func=lambda message: message.text.isdigit() and len(message.text) == 6)
def otp_verify(message: Message):
    code = message.text
    user = get_user(telegram_id=message.from_user.id)
    verify_sms = check_sms_code(user=user, code=code)
    if verify_sms:
        if get_user_job_application(user=user) is None:
            bot.send_message(chat_id=message.chat.id, text="Accountingiz muvaffaqiyatli faollashtirildi.",
                             reply_markup=default.get_job_application())
        else:
            bot.send_message(chat_id=message.chat.id, text="Accountingiz muvaffaqiyatli faollashtirildi.",
                             reply_markup=default.get_psychology_test())
    else:
        bot.send_message(chat_id=message.chat.id, text="Kod xato.\n"
                                                       "Qaytadan urinib ko'ring.")


@bot.message_handler(func=lambda message: message.text == "Job Application haqida ma'lumot olish")
def about_job_application(message: Message):
    bot.send_message(chat_id=message.chat.id, text=ABOUT_APPLICATION_MESSAGE)


@bot.message_handler(func=lambda message: message.text == "Job Application yuborish")
def job_application(message: Message):
    bot.send_message(chat_id=message.chat.id, text="Iltimos, quyidagi ma'lumotlarni to'liq va to'g'ri kiriting.",
                     reply_markup=ReplyKeyboardRemove())
    bot.send_message(chat_id=message.chat.id, text="Ismingizni kiriting:")
    bot.set_state(message.from_user.id, JobApplicationState.FIRST_NAME)


@bot.message_handler(func=lambda message: bot.get_state(message.from_user.id) == JobApplicationState.FIRST_NAME)
def first_name(message: Message):
    data = {"first_name": message.text}
    bot.add_data(message.from_user.id, message.chat.id, **data)
    bot.send_message(chat_id=message.chat.id, text="Familiyangizni kiriting:")
    bot.set_state(message.from_user.id, JobApplicationState.LAST_NAME)


@bot.message_handler(func=lambda message: bot.get_state(message.from_user.id) == JobApplicationState.LAST_NAME)
def last_name(message: Message):
    data = {"last_name": message.text}
    bot.add_data(message.from_user.id, message.chat.id, **data)
    bot.send_message(chat_id=message.chat.id, text="1-Rasmingizni yuboring(4X5 formatda):\n"
                                                   "* Rasm orqa fon oq bulishi kerak.\n"
                                                   "* Rasm Tiniq bo'lishi kerak.\n"
                     )
    bot.set_state(message.from_user.id, JobApplicationState.PHOTO_4X5)


@bot.message_handler(func=lambda message: bot.get_state(message.from_user.id) == JobApplicationState.PHOTO_4X5,
                     content_types=["photo"])
def photo_4x5(message: Message):
    try:
        data = {"photo_4x5": message.photo[-1].file_id}
        photo_path = bot.get_file(message.photo[-1].file_id).file_path

        full_path = str(BASE_DIR) + "/media/application/" + str(photo_path)
        downloaded_photo = bot.download_file(photo_path)
        with open(full_path, 'wb') as new_file:
            new_file.write(downloaded_photo)
        bot.add_data(message.from_user.id, message.chat.id, **data)
        bot.send_message(chat_id=message.chat.id, text="2-Rasmingizni yuboring(tuliq buyingiz bilan):\n"
                                                       "* Rasm orqa fon oq bulishi kerak.\n"
                                                       "* Rasm Tiniq bo'lishi kerak.\n")
        bot.set_state(message.from_user.id, JobApplicationState.PHOTO_FULL_BODY)

    except Exception as e:
        sentry_sdk.capture_exception(e)
        bot.send_message(chat_id=message.chat.id, text="Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")


@bot.message_handler(content_types=["photo"],
                     func=lambda message: bot.get_state(message.from_user.id) == JobApplicationState.PHOTO_FULL_BODY)
def photo_full(message: Message):
    try:
        data = {"photo": message.photo[-1].file_id}
        photo_path = bot.get_file(message.photo[-1].file_id).file_path

        full_path = str(BASE_DIR) + "/media/application/" + str(photo_path)
        downloaded_photo = bot.download_file(photo_path)
        with open(full_path, 'wb') as new_file:
            new_file.write(downloaded_photo)
        bot.add_data(message.from_user.id, message.chat.id, **data)
        bot.send_message(chat_id=message.chat.id, text="Bo'yingizni kiriting:")
        bot.set_state(message.from_user.id, JobApplicationState.HEIGHT)

    except Exception as e:
        sentry_sdk.capture_exception(e)
        bot.send_message(chat_id=message.chat.id, text="Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")


@bot.message_handler(func=lambda message: bot.get_state(message.from_user.id) == JobApplicationState.HEIGHT)
def height(message: Message):
    data = {"height": message.text}
    bot.add_data(message.from_user.id, message.chat.id, **data)
    bot.send_message(chat_id=message.chat.id, text="Vazningizni kiriting:")
    bot.set_state(message.from_user.id, JobApplicationState.WEIGHT)


@bot.message_handler(func=lambda message: bot.get_state(message.from_user.id) == JobApplicationState.WEIGHT)
def weight(message: Message):
    data = {"weight": message.text}
    bot.add_data(message.from_user.id, message.chat.id, **data)
    bot.send_message(chat_id=message.chat.id, text="Telefon raqamingizni kiriting:")
    bot.set_state(message.from_user.id, JobApplicationState.PHONE_NUMBER)


@bot.message_handler(func=lambda message: bot.get_state(message.from_user.id) == JobApplicationState.PHONE_NUMBER)
def phone_number(message: Message):
    data = {"phone_number": message.text}
    bot.add_data(message.from_user.id, message.chat.id, **data)
    bot.send_message(chat_id=message.chat.id, text="Emailingizni kiriting:")
    bot.set_state(message.from_user.id, JobApplicationState.EMAIL)


@bot.message_handler(func=lambda message: bot.get_state(message.from_user.id) == JobApplicationState.EMAIL)
def email(message: Message):
    data = {"email": message.text}
    bot.add_data(message.from_user.id, message.chat.id, **data)
    bot.send_message(chat_id=message.chat.id, text="Oilaviy holatingizni tanlang:",
                     reply_markup=default.get_family_status())
    bot.set_state(message.from_user.id, JobApplicationState.FAMILY_STATUS)


@bot.message_handler(func=lambda message: bot.get_state(message.from_user.id) == JobApplicationState.FAMILY_STATUS and
                                          message.text in [status[1] for status in JobApplication.Status.choices])
def family_status(message: Message):
    data = {"family_status": message.text}
    bot.add_data(message.from_user.id, message.chat.id, **data)
    bot.send_message(chat_id=message.chat.id, text="Tug'ilgan kuningizni kiriting (sana.oy.yil):\n"
                                                   "Misol uchun: [14.07.2002]", reply_markup=ReplyKeyboardRemove())
    bot.set_state(message.from_user.id, JobApplicationState.BIRTH_DATE)


@bot.message_handler(func=lambda message: bot.get_state(message.from_user.id) == JobApplicationState.BIRTH_DATE)
def birth_date(message: Message):
    data = {"birth_date": message.text}
    bot.add_data(message.from_user.id, message.chat.id, **data)
    bot.send_message(chat_id=message.chat.id, text="Manzilingizni kiriting:")
    bot.set_state(message.from_user.id, JobApplicationState.ADDRESS)


@bot.message_handler(func=lambda message: bot.get_state(message.from_user.id) == JobApplicationState.ADDRESS)
def address(message: Message):
    data = {"address": message.text}
    bot.add_data(message.from_user.id, message.chat.id, **data)
    bot.send_message(chat_id=message.chat.id, text="Ishga qabul qilinmoqchi bo'lgan lavozimingizni kiriting:")
    bot.set_state(message.from_user.id, JobApplicationState.REQUESTED_POSITION)


@bot.message_handler(func=lambda message: bot.get_state(message.from_user.id) == JobApplicationState.REQUESTED_POSITION)
def requested_position(message: Message):
    data = {"requested_position": message.text}
    bot.add_data(message.from_user.id, message.chat.id, **data)
    bot.send_message(chat_id=message.chat.id, text="Hujjat turini tanlang:", reply_markup=default.get_document_types())
    bot.set_state(message.from_user.id, JobApplicationState.APPLICANT_DOC_TYPE)


@bot.message_handler(
    func=lambda message: bot.get_state(
        message.from_user.id) == JobApplicationState.APPLICANT_DOC_TYPE and message.text in [
                             "Certificate", "Diploma"])
def applicant_doc_type(message: Message):
    with bot.retrieve_data(message.from_user.id) as data:
        if "applicant_docs" in data:
            data["applicant_docs"].append({"doc_type": message.text})
        else:
            data = {"applicant_docs": [{"doc_type": message.text}]}
    bot.add_data(message.from_user.id, message.chat.id, **data)
    bot.send_message(chat_id=message.chat.id, text="Document faylini yuboring:",
                     reply_markup=ReplyKeyboardRemove())
    bot.set_state(message.from_user.id, JobApplicationState.APPLICANT_DOC)


@bot.message_handler(func=lambda message: bot.get_state(message.from_user.id) == JobApplicationState.APPLICANT_DOC,
                     content_types=["document"])
def applicant_doc(message: Message):
    try:
        with bot.retrieve_data(message.from_user.id) as data:
            doc_count = len(data["applicant_docs"])
            data["applicant_docs"][doc_count - 1]["file"] = message.document.file_id
        bot.add_data(message.from_user.id, message.chat.id, **data)
        file_path = bot.get_file(message.document.file_id).file_path
        full_path = str(BASE_DIR) + "/media/application/applicant_docs/" + str(file_path)
        downloaded_file = bot.download_file(file_path)
        with open(full_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        bot.send_message(chat_id=message.chat.id, text="Kiritgan ma'lumotingiz qabul qilindi.",
                         reply_markup=default.next_or_again())

    except Exception as e:
        sentry_sdk.capture_exception(e)
        bot.send_message(chat_id=message.chat.id, text="Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")


@bot.message_handler(
    func=lambda message: bot.get_state(message.from_user.id) == JobApplicationState.COMPUTER_SKILL_NAME)
def computer_skill_name(message: Message):
    with bot.retrieve_data(message.from_user.id) as data:
        if "computer_skills" in data:
            data["computer_skills"].append({"name": message.text})
        else:
            data = {"computer_skills": [{"name": message.text}]}

    bot.add_data(message.from_user.id, message.chat.id, **data)
    bot.send_message(chat_id=message.chat.id, text="Bu dasturni qay darajada bilasiz:",
                     reply_markup=default.get_computer_skill_degree())
    bot.set_state(message.from_user.id, JobApplicationState.COMPUTER_SKILL_DEGREE)


@bot.message_handler(
    func=lambda message: bot.get_state(message.from_user.id) == JobApplicationState.COMPUTER_SKILL_DEGREE and
                         message.text in [degree[1] for degree in ComputerSkill.Degree.choices])
def computer_skill_degree(message: Message):
    with bot.retrieve_data(message.from_user.id) as data:
        degree_count = len(data["computer_skills"])
        data["computer_skills"][degree_count - 1]["degree"] = message.text
    bot.add_data(message.from_user.id, message.chat.id, **data)
    bot.send_message(chat_id=message.chat.id, text="Kiritgan qobilyatingiz qabul qilindi.",
                     reply_markup=default.next_or_again())


@bot.message_handler(func=lambda message: message.text == "Yana qushish")
def add_again(message: Message):
    if bot.get_state(message.from_user.id) == JobApplicationState.APPLICANT_DOC:
        bot.set_state(message.from_user.id, JobApplicationState.APPLICANT_DOC_TYPE)
        bot.send_message(chat_id=message.chat.id, text="Hujjat turini tanlang:",
                         reply_markup=default.get_document_types())
    elif bot.get_state(message.from_user.id) == JobApplicationState.COMPUTER_SKILL_DEGREE:
        bot.set_state(message.from_user.id, JobApplicationState.COMPUTER_SKILL_NAME)
        bot.send_message(chat_id=message.from_user.id, text="Dastur nomini yozing", reply_markup=ReplyKeyboardRemove())
    elif bot.get_state(message.from_user.id) == JobApplicationState.EDUCATION_COUNTRY:
        bot.set_state(message.from_user.id, JobApplicationState.EDUCATION_TITLE)
        bot.send_message(chat_id=message.chat.id, text="Oqigan ta'lim muassasangizni kiriting:")
    elif bot.get_state(message.from_user.id) == JobApplicationState.EXPERIENCE_COUNTRY:
        bot.set_state(message.from_user.id, JobApplicationState.EXPERIENCE_ORGANIZATION_NAME)
        bot.send_message(chat_id=message.chat.id, text="Ishlagan tashkilot nomini kiriting: \n")
    elif bot.get_state(message.from_user.id) == JobApplicationState.LANGUAGE_SKILL_WRITING:
        bot.set_state(message.from_user.id, JobApplicationState.LANGUAGE_SKILL_NAME)
        bot.send_message(chat_id=message.chat.id, text="Bilgan Tilningizni Nomini kiriting:")
    else:
        bot.send_message(chat_id=message.chat.id,
                         text="Iltimos, iltimos botni qaytadan ishga tushiring va har bir qadamda suralgan ma'lumotnigina kiriting.",
                         reply_markup=default.start_keyboard())
        bot.set_state(message.from_user.id, None)


@bot.message_handler(func=lambda message: message.text == "Davom etish")
def next_step(message: Message):
    if bot.get_state(message.from_user.id) == JobApplicationState.APPLICANT_DOC:
        bot.send_message(chat_id=message.chat.id, text="Kompyuterda qanday dasturlar bilan ishlashni bilasiz\n"
                                                       "Bittalab kiriting. Dastur nomini yozing: ",
                         reply_markup=ReplyKeyboardRemove())
        bot.set_state(message.from_user.id, JobApplicationState.COMPUTER_SKILL_NAME)
    elif bot.get_state(message.from_user.id) == JobApplicationState.COMPUTER_SKILL_DEGREE:
        bot.send_message(chat_id=message.chat.id, text="Oqigan ta'lim muassasangizni kiriting:",
                         reply_markup=ReplyKeyboardRemove())
        bot.set_state(message.from_user.id, JobApplicationState.EDUCATION_TITLE)
    elif bot.get_state(message.from_user.id) == JobApplicationState.EDUCATION_COUNTRY:
        bot.send_message(chat_id=message.chat.id, text="Ishlagan tashkilot nomini kiriting: \n",
                         reply_markup=ReplyKeyboardRemove())
        bot.set_state(message.from_user.id, JobApplicationState.EXPERIENCE_ORGANIZATION_NAME)
    elif bot.get_state(message.from_user.id) == JobApplicationState.EXPERIENCE_COUNTRY:
        bot.send_message(chat_id=message.chat.id, text="Bilgan Tilningizni Nomini kiriting:",
                         reply_markup=ReplyKeyboardRemove())
        bot.set_state(message.from_user.id, JobApplicationState.LANGUAGE_SKILL_NAME)
    else:
        bot.send_message(chat_id=message.chat.id,
                         text="Iltimos, iltimos botni qaytadan ishga tushiring va har bir qadamda suralgan ma'lumotnigina kiriting.",
                         reply_markup=default.start_keyboard())
        bot.set_state(message.from_user.id, None)


@bot.message_handler(func=lambda message: bot.get_state(message.from_user.id) == JobApplicationState.EDUCATION_TITLE)
def education_title(message: Message):
    with bot.retrieve_data(message.from_user.id) as data:
        if "educations" in data:
            data["educations"].append({"title": message.text})
        else:
            data = {"educations": [{"title": message.text}]}
    bot.add_data(message.from_user.id, message.chat.id, **data)
    bot.send_message(chat_id=message.chat.id, text="O'qishni boshlagan vaqtingizni kiriting (oy.yil):\n"
                                                   "Misol uchun: [07.2002]")
    bot.set_state(message.from_user.id, JobApplicationState.EDUCATION_STARTED_DATE)


@bot.message_handler(
    func=lambda message: bot.get_state(message.from_user.id) == JobApplicationState.EDUCATION_STARTED_DATE)
def education_started_date(message: Message):
    with bot.retrieve_data(message.from_user.id) as data:
        education_count = len(data["educations"])
        data["educations"][education_count - 1]["started_date"] = message.text
    bot.add_data(message.from_user.id, message.chat.id, **data)
    bot.send_message(chat_id=message.chat.id, text="O'qishni tugatgan vaqtingizni kiriting (oy.yil):\n"
                                                   "Misol uchun: [07.2010]")
    bot.set_state(message.from_user.id, JobApplicationState.EDUCATION_FINISHED_DATE)


@bot.message_handler(
    func=lambda message: bot.get_state(message.from_user.id) == JobApplicationState.EDUCATION_FINISHED_DATE)
def education_finished_date(message: Message):
    with bot.retrieve_data(message.from_user.id) as data:
        education_count = len(data["educations"])
        data["educations"][education_count - 1]["finished_date"] = message.text
    bot.add_data(message.from_user.id, message.chat.id, **data)
    bot.send_message(chat_id=message.chat.id, text="O'qish yo'nalishingizni kiriting:")
    bot.set_state(message.from_user.id, JobApplicationState.EDUCATION_DIRECTION)


@bot.message_handler(
    func=lambda message: bot.get_state(message.from_user.id) == JobApplicationState.EDUCATION_DIRECTION)
def education_direction(message: Message):
    with bot.retrieve_data(message.from_user.id) as data:
        education_count = len(data["educations"])
        data["educations"][education_count - 1]["direction"] = message.text
    bot.add_data(message.from_user.id, message.chat.id, **data)
    bot.send_message(chat_id=message.chat.id, text="O'qish davlatini kiriting:")
    bot.set_state(message.from_user.id, JobApplicationState.EDUCATION_COUNTRY)


@bot.message_handler(func=lambda message: bot.get_state(message.from_user.id) == JobApplicationState.EDUCATION_COUNTRY)
def education_country(message: Message):
    with bot.retrieve_data(message.from_user.id) as data:
        education_count = len(data["educations"])
        data["educations"][education_count - 1]["country"] = message.text
    bot.add_data(message.from_user.id, message.chat.id, **data)
    bot.send_message(chat_id=message.chat.id, text="Kiritgan Ta'lim muassasangiz qabul qilindi:",
                     reply_markup=default.next_or_again())


@bot.message_handler(
    func=lambda message: bot.get_state(message.from_user.id) == JobApplicationState.EXPERIENCE_ORGANIZATION_NAME)
def experience_organization_name(message: Message):
    with bot.retrieve_data(message.from_user.id) as data:
        if "experiences" in data:
            data["experiences"].append({"organization_name": message.text})
        else:
            data = {"experiences": [{"organization_name": message.text}]}
    bot.add_data(message.from_user.id, message.chat.id, **data)
    bot.send_message(chat_id=message.chat.id, text="Ishlagan joyingizni manzilini kiriting.")
    bot.set_state(message.from_user.id, JobApplicationState.EXPERIENCE_ORGANIZATION_ADDRESS)


@bot.message_handler(
    func=lambda message: bot.get_state(message.from_user.id) == JobApplicationState.EXPERIENCE_ORGANIZATION_ADDRESS)
def experience_organization_address(message: Message):
    with bot.retrieve_data(message.from_user.id) as data:
        experience_count = len(data["experiences"])
        data["experiences"][experience_count - 1]["organization_address"] = message.text
    bot.add_data(message.from_user.id, message.chat.id, **data)
    bot.send_message(chat_id=message.chat.id, text="Ishlagan lavozimingizni kiriting:")
    bot.set_state(message.from_user.id, JobApplicationState.EXPERIENCE_POSITION)


@bot.message_handler(
    func=lambda message: bot.get_state(message.from_user.id) == JobApplicationState.EXPERIENCE_POSITION)
def experience_position(message: Message):
    with bot.retrieve_data(message.from_user.id) as data:
        experience_count = len(data["experiences"])
        data["experiences"][experience_count - 1]["position"] = message.text
    bot.add_data(message.from_user.id, message.chat.id, **data)
    bot.send_message(chat_id=message.chat.id, text="Ish boshlagan vaqtingizni kiriting (oy.yil):\n"
                                                   "Misol uchun: [07.2011]")
    bot.set_state(message.from_user.id, JobApplicationState.EXPERIENCE_STARTED_DATE)


@bot.message_handler(
    func=lambda message: bot.get_state(message.from_user.id) == JobApplicationState.EXPERIENCE_STARTED_DATE)
def experience_started_date(message: Message):
    with bot.retrieve_data(message.from_user.id) as data:
        experience_count = len(data["experiences"])
        data["experiences"][experience_count - 1]["started_date"] = message.text
    bot.add_data(message.from_user.id, message.chat.id, **data)
    bot.send_message(chat_id=message.chat.id, text="Ish tugatgan vaqtingizni kiriting (oy.yil):\n"
                                                   "Misol uchun: [07.2014]")
    bot.set_state(message.from_user.id, JobApplicationState.EXPERIENCE_FINISHED_DATE)


@bot.message_handler(
    func=lambda message: bot.get_state(message.from_user.id) == JobApplicationState.EXPERIENCE_FINISHED_DATE)
def experience_finished_date(message: Message):
    with bot.retrieve_data(message.from_user.id) as data:
        experience_count = len(data["experiences"])
        data["experiences"][experience_count - 1]["finished_date"] = message.text
    bot.add_data(message.from_user.id, message.chat.id, **data)
    bot.send_message(chat_id=message.chat.id, text="Ish davlatini kiriting:")
    bot.set_state(message.from_user.id, JobApplicationState.EXPERIENCE_COUNTRY)


@bot.message_handler(func=lambda message: bot.get_state(message.from_user.id) == JobApplicationState.EXPERIENCE_COUNTRY)
def experience_country(message: Message):
    with bot.retrieve_data(message.from_user.id) as data:
        experience_count = len(data["experiences"])
        data["experiences"][experience_count - 1]["country"] = message.text
    bot.add_data(message.from_user.id, message.chat.id, **data)
    bot.send_message(chat_id=message.chat.id, text="Ish tashkiloti qabul qilindi",
                     reply_markup=default.next_or_again())


@bot.message_handler(
    func=lambda message: bot.get_state(message.from_user.id) == JobApplicationState.LANGUAGE_SKILL_NAME)
def language_skill_name(message: Message):
    with bot.retrieve_data(message.from_user.id) as data:
        if "language_skills" in data:
            data["language_skills"].append({"name": message.text})
        else:
            data = {"language_skills": [{"name": message.text}]}
    bot.add_data(message.from_user.id, message.chat.id, **data)
    bot.send_message(chat_id=message.chat.id, text="Bu til uchun Speaking darajangiz:",
                     reply_markup=default.get_language_skill_degree())
    bot.set_state(message.from_user.id, JobApplicationState.LANGUAGE_SKILL_SPEAKING)


@bot.message_handler(
    func=lambda message: bot.get_state(message.from_user.id) == JobApplicationState.LANGUAGE_SKILL_SPEAKING and
                         message.text in [degree[1] for degree in LanguageSkill.Degree.choices])
def language_skill_speaking(message: Message):
    with bot.retrieve_data(message.from_user.id) as data:
        language_count = len(data["language_skills"])
        data["language_skills"][language_count - 1]["speaking"] = message.text
    bot.add_data(message.from_user.id, message.chat.id, **data)
    bot.send_message(chat_id=message.chat.id, text="Bu til uchun Reading darajangiz:",
                     reply_markup=default.get_language_skill_degree())
    bot.set_state(message.from_user.id, JobApplicationState.LANGUAGE_SKILL_READING)


@bot.message_handler(
    func=lambda message: bot.get_state(message.from_user.id) == JobApplicationState.LANGUAGE_SKILL_READING and
                         message.text in [degree[1] for degree in LanguageSkill.Degree.choices])
def language_skill_reading(message: Message):
    with bot.retrieve_data(message.from_user.id) as data:
        language_count = len(data["language_skills"])
        data["language_skills"][language_count - 1]["reading"] = message.text
    bot.add_data(message.from_user.id, message.chat.id, **data)
    bot.send_message(chat_id=message.chat.id, text="Bu til uchun Writing darajangiz:",
                     reply_markup=default.get_language_skill_degree())
    bot.set_state(message.from_user.id, JobApplicationState.LANGUAGE_SKILL_WRITING)


@bot.message_handler(
    func=lambda message: bot.get_state(message.from_user.id) == JobApplicationState.LANGUAGE_SKILL_WRITING and
                         message.text in [degree[1] for degree in LanguageSkill.Degree.choices])
def language_skill_writing(message: Message):
    with bot.retrieve_data(message.from_user.id) as data:
        language_count = len(data["language_skills"])
        data["language_skills"][language_count - 1]["writing"] = message.text
    bot.add_data(message.from_user.id, message.chat.id, **data)

    bot.send_message(chat_id=message.chat.id, text="Bu til uchun Listening darajangiz:",
                     reply_markup=default.get_language_skill_degree())
    bot.set_state(message.from_user.id, JobApplicationState.LANGUAGE_SKILL_LISTENING)


@bot.message_handler(
    func=lambda message: bot.get_state(message.from_user.id) == JobApplicationState.LANGUAGE_SKILL_LISTENING and
                         message.text in [degree[1] for degree in LanguageSkill.Degree.choices])
def language_skill_listening(message: Message):
    with bot.retrieve_data(message.from_user.id) as data:
        language_count = len(data["language_skills"])
        data["language_skills"][language_count - 1]["listening"] = message.text
    bot.add_data(message.from_user.id, message.chat.id, **data)
    bot.send_message(chat_id=message.chat.id, text="Kiritgan Til qobilyatlaringiz qabul qilindi.",
                     reply_markup=default.add_again())


@bot.message_handler(func=lambda message: message.text == "Tugatish")
def finish(message: Message):
    try:

        with bot.retrieve_data(message.from_user.id) as data:
            pass
        computer_skills = "Computer Skills:\n"
        for number, computer_skill in enumerate(data["computer_skills"], 1):
            computer_skills += (f"  {number}-Skill\n"
                                f"    1. Name - {computer_skill['name']}\n"
                                f"    2. Degree - {computer_skill['degree']}\n")

        experiences = "Experiences:\n"
        for number, experience in enumerate(data["experiences"], 1):
            experiences += (f"  {number}-Experience\n"
                            f"    1. Organization name - {experience['organization_name']}\n"
                            f"    2. Organization address - {experience['organization_address']}\n"
                            f"    3. Position - {experience['position']}\n"
                            f"    4. Started date - {experience['started_date']}\n"
                            f"    5. Finished date - {experience['finished_date']}\n"
                            f"    6. Country - {experience['country']}\n")
        language_skills = "Language Skills:\n"
        for number, language_skill in enumerate(data["language_skills"], 1):
            language_skills += (
                f"  {number}-Language\n"
                f"    Langauge Name - {language_skill['name']}\n"
                f"    1. Speaking - {language_skill['speaking']}\n"
                f"    2. Reading - {language_skill['reading']}\n"
                f"    3. Writing - {language_skill['writing']}\n"
                f"    4. Listening - {language_skill['listening']}\n")

        educations = "Educations:\n"
        for number, education in enumerate(data["educations"], 1):
            educations += (
                f"  {number}-Education\n"
                f"    1. Education Name - {education['title']}\n"
                f"    2. Started date - {education['started_date']}\n"
                f"    3. Finished date - {education['finished_date']}\n"
                f"    4. Direction - {education['direction']}\n"
                f"    5. Country - {education['country']}\n")
        applicant_docs = "Applicant Docs:\n"
        for number, applicant_doc in enumerate(data["applicant_docs"], 1):
            applicant_docs += (
                f"  {number}-Doc\n"
                f"    1. File - {applicant_doc['file']}\n"
                f"    2. Type - {applicant_doc['doc_type']}\n")

        photo_path = bot.get_file(data['photo']).file_path
        photo_4x5_path = bot.get_file(data['photo_4x5']).file_path
        full_path_photo = str(BASE_DIR) + "/media/application/" + str(photo_path)
        full_path_photo_4x5 = str(BASE_DIR) + "/media/application/" + str(photo_4x5_path)

        with open(full_path_photo_4x5, 'rb') as image:
            bot.send_message(chat_id=message.chat.id, text="Sizning 1-yuborgan, 4x5 formatdagi rasmingiz:")
            bot.send_photo(chat_id=message.chat.id, photo=image)

        with open(full_path_photo, 'rb') as image:
            bot.send_message(chat_id=message.chat.id, text="Sizning 2-yuborgan tuliq bo'y formatdagi rasmingiz:")
            bot.send_photo(chat_id=message.chat.id, photo=image)

        message_template = f"First name: {data['first_name']}\n" \
                           f"Last name: {data['last_name']}\n" \
                           f"Height: {data['height']}\n" \
                           f"Weight: {data['weight']}\n" \
                           f"Phone number: {data['phone_number']}\n" \
                           f"Email: {data['email']}\n" \
                           f"Family status: {data['family_status']}\n" \
                           f"Birth date: {data['birth_date']}\n" \
                           f"Address: {data['address']}\n" \
                           f"Requested position: {data['requested_position']}\n" \
                           f"{computer_skills}\n" \
                           f"{experiences}\n" \
                           f"{educations}\n" \
                           f"{language_skills}\n" \
                           f"{applicant_docs}\n"

        bot.send_message(chat_id=message.chat.id, text=message_template)
        bot.send_message(chat_id=message.chat.id, text="Kiritgan ma'lumotlaringizni tasdiqlang\n",
                         reply_markup=default.get_application_verify_keyboard())
    except Exception as e:
        sentry_sdk.capture_exception(e)
        bot.send_message(chat_id=message.chat.id, text="Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.",
                         reply_markup=default.start_keyboard())


@bot.message_handler(func=lambda message: message.text == "Tasdiqlash")
def verify_application(message: Message):
    user = get_user(telegram_id=message.from_user.id)
    with bot.retrieve_data(message.from_user.id) as data:
        try:

            photo_path = bot.get_file(data['photo']).file_path
            full_path_photo = "/application/" + str(photo_path)

            photo_4x5_path = bot.get_file(data['photo_4x5']).file_path
            full_path_photo_4x5 = "/application/" + str(photo_4x5_path)

            application = create_job_application(user=user, first_name=data["first_name"],
                                                 last_name=data["last_name"], height=data["height"],
                                                 weight=data["weight"], phone_number=data["phone_number"],
                                                 email=data["email"], family_status=data["family_status"],
                                                 birth_date=data["birth_date"], address=data["address"],
                                                 requested_position=data["requested_position"],
                                                 user_photo=full_path_photo,
                                                 user_4x5_photo=full_path_photo_4x5)
            for computer_skill in data["computer_skills"]:
                create_computer_skill(application=application, name=computer_skill["name"],
                                      degree=computer_skill["degree"])

            for experience in data["experiences"]:
                create_experience(application=application, started_date=experience["started_date"],
                                  finished_date=experience["finished_date"],
                                  organization_name=experience["organization_name"],
                                  organization_address=experience["organization_address"],
                                  position=experience["position"], country=experience["country"])

            for language_skill in data["language_skills"]:
                create_language_skill(application=application, name=language_skill["name"],
                                      speaking=language_skill["speaking"],
                                      reading=language_skill["reading"], writing=language_skill["writing"],
                                      listening=language_skill["listening"])

            for education in data["educations"]:
                create_education(application=application, started_date=education["started_date"],
                                 finished_date=education["finished_date"], title=education["title"],
                                 direction=education["direction"], country=education["country"])

            for applicant_doc in data["applicant_docs"]:
                file_path = bot.get_file(applicant_doc["file"]).file_path
                full_path_document = "/application/applicant_docs/" + str(file_path)
                create_applicant_document(application=application, type=applicant_doc["doc_type"],
                                          file=full_path_document)
            generate_html(application=application, computer_skills=application.computer_skills.all(),
                          experiences=application.experiences.all(), educations=application.educations.all(),
                          language_skills=application.language_skills.all(),
                          applicant_docs=application.docs.all())

            pdf_file = convert_text_to_pdf("application.pdf")
            document_pusher(pdf_file)
            email_sender(file_name=pdf_file)
            bot.send_message(chat_id=message.chat.id, text="Sizning ma'lumotlaringiz qabul qilindi.✅\n"
                                                           "Biz siz bilan tez orada bog'lanamiz.",
                             reply_markup=ReplyKeyboardRemove())

            bot.send_message(chat_id=message.chat.id, text="Psixologik Testni yechib kuring.",
                             reply_markup=default.get_psychology_test())
        except ValidationError:
            bot.send_message(chat_id=message.chat.id, text="Siz allaqachon appplication yuborgansiz.")
            return
        except Exception as e:
            sentry_sdk.capture_exception(e)
            bot.send_message(chat_id=message.chat.id, text="Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.",
                             reply_markup=default.start_keyboard())


@bot.message_handler(func=lambda message: message.text == "Bekor qilish")
def cancel_application(message: Message):
    bot.send_message(chat_id=message.chat.id, text="Sizning ma'lumotlaringiz qabul qilinmadi.\n"
                                                   "Iltimos, qaytadan urinib ko'ring.",
                     reply_markup=default.get_job_application())


@bot.message_handler(func=lambda message: message.text == "Psixologik Testlar")
def psychology_test(message: Message):
    bot.set_state(message.from_user.id, TestState.QUESTION)
    tests = get_tests()
    keyboards = inline.get_test_keyboard(tests)
    bot.send_message(chat_id=message.chat.id, text="Psixologik Testlar", reply_markup=ReplyKeyboardRemove())
    bot.send_message(chat_id=message.chat.id, text="Quyidagi testlardan birontasini tanlab yechishingiz mumkin.",
                     reply_markup=keyboards)


@bot.message_handler(func=lambda message: message.text == "Psixologik Test haqida ma'lumot olish")
def about_psychology_test(message: Message):
    bot.send_message(chat_id=message.chat.id, text=ABOUT_TEST_MESSAGE)


@bot.callback_query_handler(func=lambda call: call.data.startswith("test_"))
def test(call):
    try:

        if bot.get_state(call.from_user.id) == TestState.QUESTION:
            bot.set_state(call.from_user.id, TestState.ANSWER)
            test_id = call.data.split("_")[1]
            with bot.retrieve_data(call.from_user.id) as data:
                questions = list(get_questions(test_id=test_id))
                data["test"] = {"id": test_id, "result": 0, "questions": questions}
                question = data["test"]["questions"].pop(0)
                bot.add_data(call.from_user.id, call.message.chat.id, **data)

            bot.send_message(chat_id=call.message.chat.id, text=f"{question.index}. {question.text}",
                             reply_markup=inline.get_answer_keyboard(question.answers.all()))
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          reply_markup=None)
        else:
            bot.answer_callback_query(callback_query_id=call.id, text="Siz allaqachon testni yechib bo'lgansiz.")
    except Exception as e:
        sentry_sdk.capture_exception(e)
        bot.answer_callback_query(callback_query_id=call.id,
                                  text="Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")


@bot.callback_query_handler(func=lambda call: call.data.startswith("answer_"))
def answer(call):
    try:

        if bot.get_state(call.from_user.id) == TestState.ANSWER:
            answer_id = call.data.split("_")[1]
            with bot.retrieve_data(call.from_user.id) as data:
                answer = get_test_answer(answer_id=answer_id)
                data["test"]["result"] += answer.ball
                bot.add_data(call.from_user.id, call.message.chat.id, **data)
            if len(data["test"]["questions"]) > 0:
                question = data["test"]["questions"].pop(0)
                bot.send_message(chat_id=call.message.chat.id, text=question.text,
                                 reply_markup=inline.get_answer_keyboard(question.answers.all()))
                bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              reply_markup=None)
            else:
                bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              reply_markup=None)
                test = get_test(data["test"]["id"])
                user = get_user(telegram_id=call.from_user.id)
                user_result = create_user_test_result(user=user,
                                                      test=test,
                                                      total_ball=data["test"]["result"])
                application = user.jobapplication
                bot.send_message(chat_id=call.message.chat.id, text="Sizning test natijangiz hisoblanyapti...\n"
                                                                    "Iltimos kuting !!!")
                generate_html(application=application, computer_skills=application.computer_skills.all(),
                              experiences=application.experiences.all(), educations=application.educations.all(),
                              language_skills=application.language_skills.all(),
                              applicant_docs=application.docs.all(), test_result=user_result)

                pdf_file = convert_text_to_pdf("application_test.pdf")
                document_pusher(pdf_file)
                email_sender(file_name=pdf_file)

                bot.send_message(chat_id=call.message.chat.id, text="Sizning test natijangiz: "
                                                                    f"{user_result.total_ball} ball.")
                ball_range = get_ball_range(total_ball=user_result.total_ball, test_id=test.id)
                bot.send_message(chat_id=call.message.chat.id, text="Siz uchun psixologni tavsiyasi\n"
                                                                    f"{ball_range.description}",
                                 reply_markup=default.get_psychology_test())

                bot.set_state(call.from_user.id, None)
        else:
            bot.answer_callback_query(callback_query_id=call.id, text="Siz boshqa holatda qolib ketgansiz.\n",
                                      show_alert=True)
            bot.send_message(chat_id=call.message.chat.id, text="Botni qayta ishga tushiring. /start",
                             reply_markup=default.start_keyboard())
    except Exception as e:
        sentry_sdk.capture_exception(e)
        bot.answer_callback_query(callback_query_id=call.id,
                                  text="Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")


class Command(BaseCommand):
    help = 'Run Telegram bot'

    def handle(self, *args, **options):
        bot.infinity_polling()
