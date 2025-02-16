import requests
import os
import logging
from retrying import retry
from dotenv import load_dotenv

#Скрыть токен, для безопасности
load_dotenv()
TOKEN = os.getenv('YANDEX_DISK_TOKEN')

#Делаем логи, для простоты отслеживания событий
logging.basicConfig(level=logging.INFO)





class YaUploader:
    def __init__(self, token):
        #Добавим основные параметры, которые будут повторяться
        if not token:
            raise ValueError("Токен доступа не может быть пустым")
        self.token = token
        self.base_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'OAuth {token}'
        }

    #Добавим обработку ошибок HTTP-запросов.
    def create_folder(self, path):
        """
        Создаёт папку на Яндекс Диске по указанному пути, если она не существует.
        """
        response = requests.get(f'{self.base_url}?path={path}', headers=self.headers)
        if response.status_code == 200:
            logging.info(f'Папка "{path}" уже существует.')
            return True
        elif response.status_code == 404:
            try:
                response = requests.put(f'{self.base_url}?path={path}', headers=self.headers)
                response.raise_for_status()
                logging.info(f'Папка "{path}" успешно создана.')
                return True
            except requests.exceptions.HTTPError as err:
                logging.error(f'Ошибка при создании папки: {err}')
                return False
        else:
            logging.error(f'Не удалось проверить наличие папки "{path}". Ошибка: {response.status_code}')
            return False

    #Добавим декоратор для исключения ошибок
    @retry(stop_max_attempt_number=3, wait_fixed=2000)
    def upload_photos_to_yd(self, path, url_file, name):
        """
        Загружает файл по URL на Яндекс.Диск.
        """
        try:
            upload_url = f"{self.base_url}/upload"
            params = {"path": f'/{path}/{name}', 'url': url_file, "overwrite": "true"}
            response = requests.post(upload_url, headers=self.headers, params=params)
            response.raise_for_status()
            logging.info(f'Файл "{name}" загружен в папку "{path}".')
            return True
        except requests.exceptions.HTTPError as err:
            logging.error(f'Ошибка при загрузке файла "{name}": {err}')
            return False