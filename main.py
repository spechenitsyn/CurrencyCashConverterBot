import telebot
from currency_converter import CurrencyConverter
from telebot.types import Message, CallbackQuery
from telebot import types

TOKEN = '6052791660:AAHS-aftaNbqQfUmcmVc8Kqwf4czz26sJYY'
bot = telebot.TeleBot(TOKEN)

curr = CurrencyConverter()
money = 0


@bot.message_handler(commands=['start'])
def start(message: Message):
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}! Я помогу тебе сконвертировать '
                                      f'все известные валюты. Введи сумму денег, которую нужно конвертировать: ')
    bot.register_next_step_handler(message, input_data)


def input_data(message: Message):
    global money
    try:
        money = int(message.text.rstrip())
    except ValueError:
        bot.send_message(message.chat.id, 'Неверный формат ввода. Попробуйте заново')
        bot.register_next_step_handler(message, input_data)
        return
    if money > 0:
        markup = types.InlineKeyboardMarkup(row_width=3)
        btn1 = types.InlineKeyboardButton('USD/GBP', callback_data='usd/gbp')
        btn2 = types.InlineKeyboardButton('USD/EUR', callback_data='usd/eur')
        btn3 = types.InlineKeyboardButton('EUR/USD', callback_data='eur/usd')
        btn4 = types.InlineKeyboardButton('Другие валюты', callback_data='else')
        markup.add(btn1, btn2, btn3, btn4)
        bot.send_message(message.chat.id, 'Выберите вариант конвертации', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Сумма должна быть больше 0. Введите корректное значение.')
        bot.register_next_step_handler(message, input_data)


@bot.callback_query_handler(func=lambda call: True)
def callback(call: CallbackQuery):
    if call.data != 'else':
        val = call.data.upper().split('/')
        conv_res = curr.convert(money, val[0], val[1])
        bot.send_message(call.message.chat.id, f'Результат конвертации: {round(conv_res, 2)} {val[1]}. '
                                               f'Можете попробовать ещё')
        bot.register_next_step_handler(call.message, input_data)
    else:
        bot.send_message(call.message.chat.id, 'Введите пару валют через слэш (/)')
        bot.register_next_step_handler(call.message, user_currency)


def user_currency(message: Message):
    try:
        user_curr = message.text.rstrip().upper().split('/')
        conv_res = curr.convert(money, user_curr[0], user_curr[1])
        bot.send_message(message.chat.id, f'Результат конвертации: {round(conv_res, 2)} {user_curr[1]}')
    except Exception:
        bot.send_message(message.chat.id, 'Пара валют введена в некорректном формате. Попробуйте ещё')
        bot.register_next_step_handler(message, user_currency)


bot.polling(none_stop=True)