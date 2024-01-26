from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from bot.models import JobApplication, ComputerSkill, LanguageSkill


def get_contact_phone():
    keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button = KeyboardButton(text="Telefon raqamni yuborish", request_contact=True)
    keyboard.add(button)
    return keyboard


def get_job_application():
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button_about = KeyboardButton(text="Job Application haqida ma'lumot olish")
    button_application = KeyboardButton(text="Job Application yuborish")
    keyboard.add(button_about, button_application)
    return keyboard


def get_family_status():
    keyboard = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    for status in JobApplication.Status.choices:
        keyboard.add(KeyboardButton(text=str(status[1])))
    return keyboard


def get_document_types():
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button_passport = KeyboardButton(text="Certificate")
    button_id_card = KeyboardButton(text="Diploma")
    keyboard.add(button_passport, button_id_card)
    return keyboard


def get_computer_skill_degree():
    keyboard = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    for degree in ComputerSkill.Degree.choices:
        keyboard.add(KeyboardButton(text=str(degree[1])))
    return keyboard


def next_or_again():
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button_next = KeyboardButton(text="Davom etish")
    button_again = KeyboardButton(text="Yana qushish")
    keyboard.add(button_next, button_again)
    return keyboard


def add_again():
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button_again = KeyboardButton(text="Yana qushish")
    button_finish = KeyboardButton(text="Tugatish")
    keyboard.add(button_again, button_finish)
    return keyboard


def start_keyboard():
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button_start = KeyboardButton(text="/start")
    keyboard.add(button_start)
    return keyboard


def get_language_skill_degree():
    keyboard = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    for degree in LanguageSkill.Degree.choices:
        keyboard.add(KeyboardButton(text=str(degree[1])))
    return keyboard


def get_application_verify_keyboard():
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button_verify = KeyboardButton(text="Tasdiqlash")
    button_cancel = KeyboardButton(text="Bekor qilish")
    keyboard.add(button_verify, button_cancel)
    return keyboard


def get_psychology_test():
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button_about = KeyboardButton(text="Psixologik Test haqida ma'lumot olish")
    button_start = KeyboardButton(text="Psixologik Testlar")
    keyboard.add(button_start, button_about)
    return keyboard
