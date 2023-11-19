

from datetime import datetime


def write_log(file, text: str):
    with open(file, 'a', encoding="utf-8") as file:
        file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\t\t{text}\n")
