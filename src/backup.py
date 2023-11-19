import os
import zipfile
from datetime import datetime


class Backup:
    def __init__(self) -> None:
        self.__file_zip = None

    def make_zip(self) -> str:
        file_backup = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        path = f'./tmp/{file_backup}'

        zipf = zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED)
        self.__zip_dir('data/', zipf)
        zipf.close()

        self.__file_zip = path
        return self.__file_zip

    def __zip_dir(self, path, ziph):
        # ziph is zipfile handle
        for root, dirs, files in os.walk(path):
            for file in files:
                ziph.write(os.path.join(root, file))

    def remove_backups_file(self):
        if self.__file_zip:
            os.remove(self.__file_zip)
