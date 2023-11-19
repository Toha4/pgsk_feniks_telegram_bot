from data_base import UserStatus
from data_types import User
from loging import write_log


def send_admins_request(bot, user_id) -> bool:
    """ 
    Отправка запроса на регистрацию пользователя администраторам.
    Если администраторов нет, возвращает False.
    """

    from main import db

    admin_ids = db.user_table.get_admin_ids()

    if not admin_ids:
        return False

    text_request = 'Запрос на регистрацию пользователя'

    user = db.user_table.get_user(user_id)
    if user:
        text_request += f'\n{user_info_text(user)}'
        text_request += f'\n\nКоманда для добавления /add {user.id}'


    for admin in admin_ids:
        bot.send_message(admin[0], text_request)

    return True


def user_info_text(user: User) -> str:
    """ Получение информации о пользователе в виде строки """

    return (
        f'user_id: {user.user_id}'
        f'\nusername: {user.tg_username}'
        f'\nИмя: {user.name}'
        f'\nНомер гаража: {user.garage_number}'
        f'\nНомер тел.: {user.phone_number}'
        f'\nДата регистрации: {user.date_create}'
        f'\nСтатус: {UserStatus(user.status).name}'
        f'\nАдмин: {bool(user.is_admin)}'
    )


def user_all_text() -> str:
    """ Получение списка всех пользователей в виде строки """

    from main import db

    users = 'Список всех пользователей: \nid\tИмя\tНомер гаража\tСтатус'

    all_users = db.user_table.get_all_users()
    for user in all_users:
        users += f'\n{user.id}\t{user.name}\t{user.garage_number}\t{UserStatus(user.status).name}'

    return users


def write_open_log(file, user_id):
    """ Запись в файл лога об открытии шлагбаума """

    from main import db

    user = db.user_table.get_user(user_id)

    text = ''

    if user:
        text = f'{user.id}\t{user.garage_number}\t{user.name}'
    else:
        text = 'Пользователь не найден'

    write_log(file, text)
