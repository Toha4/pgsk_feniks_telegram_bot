from datetime import datetime


class MyLogger:
    def __init__(self, file) -> None:
        self.__file = file

    def write_log(self, text: str):
        """ Запись лога в файл """

        with open(self.__file, 'a', encoding="utf-8") as file:
            file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\t{text}\n")

    def read_log_in_list(self, limit_last_row: int | None = None) -> list:
        """ Считывание лога в list """

        rows = []

        with open(self.__file, 'r', encoding="utf-8") as file:
            rows = file.readlines()
            
        if limit_last_row and len(rows) > limit_last_row:
            return rows[-limit_last_row:]
        
        return rows
