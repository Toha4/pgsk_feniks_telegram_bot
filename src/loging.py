

from datetime import datetime


def write_log(file, text: str):
    path_to_file_log = f'./data/{file}'
    with open(path_to_file_log, 'a', encoding="utf-8") as file:
        file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\t{text}\n")
