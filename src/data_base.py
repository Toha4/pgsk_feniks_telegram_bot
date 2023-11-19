from enum import Enum
from pathlib import Path
import sqlite3
from datetime import datetime

from data_types import User, UserShort


class UserStatus(Enum):
    REGISTRATION = 0
    ACTIVE = 1
    DEBTOR = 2
    BLOCKED = 3


class DataBase:
    def __init__(self, db_file) -> None:
        self.__db_file = f'./data/{db_file}'

        self.__check_db()

        self.__connection = self.__sqlite_connect()
       
        self.user_table = UserTable(self.__connection)

    def __sqlite_connect(self):
        connect = sqlite3.connect(self.__db_file, check_same_thread=False)
        return connect


    def __check_db(self):
        """ Проверка наличия БД, и создания при отсутствии """

        db = Path(self.__db_file)
        try:
            db.resolve(strict=True)
        except FileNotFoundError:
            print("Database not found, trying to create a new one.")
            self.__init_sqlite()


    def __init_sqlite(self):
        """ Инициализация базы данных при первом запуске """

        try:
            conn = self.__sqlite_connect()
            c = conn.cursor()
            c.execute(
                '''
                CREATE TABLE "users" (
                    `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, 
                    `user_id` INTEGER NOT NULL UNIQUE, 
                    `tg_username` TEXT, `name` TEXT, 
                    `phone_number` TEXT, 
                    `garage_number` INTEGER, 
                    `date_create` TEXT, 
                    `status` INTEGER NOT NULL DEFAULT 0, 
                    `is_admin` INTEGER NOT NULL DEFAULT 0 
                )
                '''
            )
            
            conn.commit()
            conn.close()

            print("Success.")
        except Exception as e:
            print("Error when creating database : ", e.__repr__(), e.args)


class UserTable():
    """ Класс для работы с таблицей users """

    def __init__(self, connection) -> None:
        self.__connection = connection
        self.__cursor = self.__connection.cursor()

    def add_user(self, user_id, tg_user_name, name, garage_number, phone_number) -> bool:
        """ Добавление новго пользователя. Если пользователь был добавлен в качестве администратора, возвращается True """

        date_create = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        is_admin = False
        status = UserStatus.REGISTRATION

        if self.users_emty():
            is_admin = True
            status = UserStatus.ACTIVE


        with self.__connection:
            self.__cursor.execute(
                'INSERT INTO `users` (`user_id`, `tg_username`, `name`, `phone_number`, `garage_number`, `date_create`, `is_admin`, `status`) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (user_id, tg_user_name, name, phone_number, garage_number, date_create, is_admin, status.value)
            )

        return is_admin

    def users_emty(self) -> bool:
        with self.__connection:
            result = self.__cursor.execute('SELECT COUNT(*) FROM `users`').fetchall()

        return result[0][0] == 0


    def user_exist(self, user_id):
        with self.__connection:
            result = self.__cursor.execute('SELECT * FROM `users` WHERE `user_id` = ?', (user_id,)).fetchall()

            return bool(len(result))
        
    def get_admin_ids(self):
        with self.__connection:
            return self.__cursor.execute('SELECT `user_id` FROM `users` WHERE `is_admin` = 1').fetchall()
        
    def user_is_active(self, user_id):
        with self.__connection:
            result = self.__cursor.execute('SELECT `status` FROM `users` WHERE `user_id` = ?', (user_id,)).fetchone()[0]

            return result == UserStatus.ACTIVE.value
        
    def user_set_status(self, id, status: UserStatus) -> int | None:
        with self.__connection:
            self.__cursor.execute('UPDATE `users` SET `status` = ? WHERE `id` = ?', (status.value, id,))
        
        return self.get_user_id(id)

    def get_user_id(self, id) -> int | None:
        user_id = None

        with self.__connection:
            user_id = self.__cursor.execute('SELECT `user_id` FROM `users` WHERE `id` = ?', (id,)).fetchone()[0]

        return user_id

    def user_is_admin(self, user_id) -> bool:
        is_admin = False
        with self.__connection:
            result = self.__cursor.execute('SELECT `is_admin` FROM `users` WHERE `user_id` = ?', (user_id,)).fetchone()
            if result:
                is_admin = bool(result[0])

        return is_admin

    def get_user(self, user_id, by_id=False) -> User | None:

        find_field = '[user_id]'
        if by_id:
            find_field = '[id]'
            

        with self.__connection:
            result = self.__cursor.execute(
                f'''
                SELECT `id`, `user_id`, `tg_username`, `name`, `phone_number`, `garage_number`, `date_create`, `status`, `is_admin` 
                FROM `users` WHERE {find_field} = ?
                ''',
                (user_id,)
            ).fetchone()

        if result:
            return User(
            id=result[0],
            user_id=result[1],
            tg_username=result[2],
            name=result[3],
            phone_number=result[4],
            garage_number=result[5],
            date_create=result[6],
            status=result[7],
            is_admin=result[8]
        )
        
        return None

    def get_all_users(self) -> list[UserShort]:
        users = []

        with self.__connection:
            result = self.__cursor.execute('SELECT `id`, `name`, `garage_number`, `status`, `is_admin` FROM `users`').fetchall()
        
            for row in result:
                users.append(
                    UserShort(id=row[0], name=row[1], garage_number=row[2], status=row[3], is_admin=row[4])
                )
        
        return users 
    