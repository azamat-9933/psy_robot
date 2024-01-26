from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_test_keyboard(tests):
    keyboard = InlineKeyboardMarkup(row_width=2)
    for test in tests:
        keyboard.add(
            InlineKeyboardButton(text=f"{test.title} - QC: {test.question_count}", callback_data=f"test_{test.id}",
                                 one_time_keyboard=True))
    return keyboard


def get_answer_keyboard(answers):
    keyboard = InlineKeyboardMarkup(row_width=2)
    for answer in answers:
        keyboard.add(
            InlineKeyboardButton(text=answer.text, callback_data=f"answer_{answer.id}"))
    return keyboard
