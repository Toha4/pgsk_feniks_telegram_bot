import os
from dotenv import load_dotenv
from pathlib import Path
import telebot
from telebot import types
from backup import Backup

from barrier_relay import open_barrier
from data_base import DataBase, UserStatus

from help import HELP_ADMIN, HELP_USER
from logger import MyLogger
import markups as nav
from utils import get_log, send_admins_request, user_all_text, user_info_text, write_open_log


load_dotenv()

API_TOKEN = os.getenv('API_TOKEN', '')
BARRIER_RELAY_URL = os.getenv('BARRIER_RELAY_URL', '')
BARRIER_RELAY_USER = os.getenv('BARRIER_RELAY_USER', '')
BARRIER_RELAY_PASSWORD = os.getenv('BARRIER_RELAY_PASSWORD', '')
DB_FILE = os.getenv('DB_FILE', 'db.db3')
LOG_OPEN_FILE = os.getenv('LOG_OPEN_FILE', 'open.log')

Path("./data").mkdir(exist_ok=True)
Path("./tmp").mkdir(exist_ok=True)

bot = telebot.TeleBot(API_TOKEN)

db = DataBase(DB_FILE)

open_logger = MyLogger(f'./data/{LOG_OPEN_FILE}')


""" Регистрация """

@bot.message_handler(commands=['start'])
def start(message):
    # Ищем пользователя в БД, если нет, то регистрируем
    if not db.user_table.user_exist(message.from_user.id):
        bot.send_message(message.chat.id, 'Для использования бота вам необходимо зарегистрироваться. Введите ваше имя')
        bot.register_next_step_handler(message, get_name)
    else:
        if db.user_table.user_is_active(message.from_user.id):
            bot.send_message(message.chat.id, f'Вы уже зарегистрированы!', reply_markup=nav.mainMenu)
        else:
            bot.send_message(message.chat.id, f'Дождитесь пока администраторы подтвердят ваши данные!')


def get_name(message):
    name = message.text.strip()

    bot.send_message(message.chat.id, 'Введите номер гаража')
    bot.register_next_step_handler(message, get_garage_number, name)


def get_garage_number(message, name):
    garage_number = message.text.strip()

    if garage_number.isdigit() and (int(garage_number) > 0 and int(garage_number) <= 92):
        bot.send_message(message.chat.id, 'Введите ваш номер телефона')
        bot.register_next_step_handler(message, get_phone_number, name, garage_number)
    else:
        bot.send_message(message.chat.id, "Некоректный ввод\nДолжно быть число от 1 до 92")
        bot.register_next_step_handler(message, get_garage_number, name)


def get_phone_number(message, name, garage_number):
    phone_number = message.text.strip()

    text_user_data = f'Имя: {name} \nНомер гаража: {garage_number} \nНомер тел.: {phone_number}'

    markup = types.InlineKeyboardMarkup()
    button_no = types.InlineKeyboardButton('Нет', callback_data=f'no|{name}|{garage_number}|{phone_number}')
    button_yes = types.InlineKeyboardButton('Да', callback_data=f'yes|{name}|{garage_number}|{phone_number}')
    
    markup.row(button_no, button_yes)

    bot.send_message(message.chat.id, f'Верны ли данные? \n{text_user_data}', reply_markup=markup)
          

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    answer, name, garage_number, phone_number = call.data.split('|')
    if answer =='yes':
        is_added_admin = db.user_table.add_user(call.from_user.id, call.from_user.username, name, garage_number, phone_number)
        
        if not is_added_admin:
            send_admins_request(bot, call.from_user.id)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Данные отправлены на проверку администраторам.')
        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Пользователь добавлен. Вам назначены права администратора!')
            bot.send_message(call.message.chat.id, f'Для просмотра всех команд введите /help!', reply_markup=nav.mainMenu)
    else:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Регистрация отменена. Для повторной регистрации введите /start.')


@bot.message_handler(commands=['help'])
def help(message):
    help_text = ''

    if db.user_table.user_is_admin(message.from_user.id):
        help_text = f'{HELP_USER}\n{HELP_ADMIN}'
    else:
        help_text = HELP_USER
        
    bot.send_message(message.chat.id, help_text)


""" Обработка команд пользователя """

@bot.message_handler(commands=['open'])
def open_(message):
    if not db.user_table.user_is_active(message.from_user.id):
        bot.send_message(message.chat.id, 'Вам запрещено открывать шлагбаум!')
        return

    if open_barrier(BARRIER_RELAY_URL, BARRIER_RELAY_USER, BARRIER_RELAY_PASSWORD):
        bot.send_message(message.chat.id, 'Шлагбаум открыт!')
        write_open_log(open_logger, message.from_user.id)


""" Обработка команд администратора """

@bot.message_handler(commands=['add'])
def add_user(message):
    if not db.user_table.user_is_admin(message.from_user.id):
        return

    try:
        id = message.text.split(' ')[1]
        user_id = db.user_table.user_set_status(id, status=UserStatus.ACTIVE)

        if user_id:
            bot.send_message(
                user_id,
                'Заявка одобрена. Можете пользоваться ботом. Для получение списка команд введите /help.',
                reply_markup=nav.mainMenu
            )
            bot.send_message(message.chat.id, 'Пользователь добавлен')
    except:
        bot.send_message(message.chat.id, 'Неверная команда')


@bot.message_handler(commands=['all_users'])
def all_users(message):
    if not db.user_table.user_is_admin(message.from_user.id):
        return
    
    all_user_str = user_all_text()
    bot.send_message(message.chat.id, all_user_str)


@bot.message_handler(commands=['userinfo'])
def user_info(message):
    if not db.user_table.user_is_admin(message.from_user.id):
        return
    
    try:
        id = message.text.split(' ')[1]
        user = db.user_table.get_user(id, by_id=True)

        if user:
            bot.send_message(message.chat.id, user_info_text(user))
        else:
            bot.send_message(message.chat.id, 'Пользователь не найден')
    except:
        bot.send_message(message.chat.id, 'Неверная команда')


@bot.message_handler(commands=['userblock'])
def user_userblock(message):
    if not db.user_table.user_is_admin(message.from_user.id):
        return
    
    try:
        id = message.text.split(' ')[1]
        user_id = db.user_table.user_set_status(id, status=UserStatus.BLOCKED)

        if user_id:
            bot.send_message(message.chat.id, 'Пользователь заблокирован')
        else:
            bot.send_message(message.chat.id, 'Пользователь не найден')
    except:
        bot.send_message(message.chat.id, 'Неверная команда')


@bot.message_handler(commands=['log'])
def log(message):
    if not db.user_table.user_is_admin(message.from_user.id):
        return
    
    try:
        log_limit = 20

        args = message.text.split(' ')
        if len(args) >= 2:
            log_limit = int(args[1])

        log = get_log(open_logger, log_limit)
        bot.send_message(message.chat.id, log)
    except:
        bot.send_message(message.chat.id, 'Неверная команда')


@bot.message_handler(commands=['backups'])
def backups(message):
    if not db.user_table.user_is_admin(message.from_user.id):
        return
    
    # Закрываем БД, делаем zip файл, открываем БД
    db.close()
    backup = Backup()
    file = backup.make_zip()
    db.connect()

    # Отправляем файл zip
    with open(file, 'rb') as document:
        bot.send_document(message.chat.id, document)

    # Удаляем файл zip
    backup.remove_backups_file()
    

""" Обработка текста """

@bot.message_handler()
def info(message):
    if message.text == 'Открыть шлагбаум':
        open_from_button(message)
    else:
        bot.send_message(message.chat.id, 'Я глупый бот, принимаю только команды. Введите /help для получение списка команд.')


def open_from_button(message):    
    if not db.user_table.user_is_active(message.from_user.id):
        bot.send_message(message.chat.id, 'Вам запрещено открывать шлагбаум!')
        return

    result_open = open_barrier(BARRIER_RELAY_URL, BARRIER_RELAY_USER, BARRIER_RELAY_PASSWORD)
    if result_open:
        bot.send_message(message.chat.id, 'Шлагбаум открыт!')
        write_open_log(open_logger, message.from_user.id)


if __name__ == "__main__":
    bot.polling(non_stop=True)
