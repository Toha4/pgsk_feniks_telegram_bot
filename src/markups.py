from telebot import types


mainMenu = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn_open = types.KeyboardButton('Открыть шлагбаум')
mainMenu.add(btn_open)