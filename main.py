import requests
import os
import logging
from retrying import retry

#Делаем логи, для простоты отслеживания событий
logging.basicConfig(level=logging.INFO)

#Скрыть токен, для безопасности
TOKEN = os.getenv('YANDEX_DISK_TOKEN')


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



def get_sub_breeds(breed):
    """
    Получает список подпород для указанной породы.
    """
    try:
        result = requests.get(f'https://dog.ceo/api/breed/{breed}/list')
        result.raise_for_status()
        return result.json().get('message', [])
    except (requests.exceptions.HTTPError, ValueError) as err:
        logging.error(f'Ошибка при получении подпород для "{breed}": {err}')
        return []



def get_urls(breed, sub_breeds):
    """
    Получает список URL случайных изображений для породы и ее подпород.
    """
    url_images = []
    if sub_breeds:
        for sub_breed in sub_breeds:
            res = requests.get(f"https://dog.ceo/api/breed/{breed}/{sub_breed}/images/random")
            sub_breed_urls = res.json().get('message')
            url_images.append(sub_breed_urls)
    else:
        url_images.append(requests.get(f"https://dog.ceo/api/breed/{breed}/images/random").json().get('message'))
    return url_images

#
def upload_images(breed, folder_name):
    """
    Загружает изображения для породы и ее подпород на Яндекс.Диск.
    """
    sub_breeds = get_sub_breeds(breed)
    urls = get_urls(breed, sub_breeds)
    yandex_client = YaUploader(TOKEN)

    #Создание папки на Я.Диске
    if not yandex_client.create_folder(folder_name):
        logging.error(f'Не удалось создать папку "{folder_name}".')
        return False

    #Загрузка изображений
    for url in urls:
        if url:
            part_name = url.split('/')
            name = '_'.join([part_name[-2], part_name[-1]])
            if not yandex_client.upload_photos_to_yd(folder_name, url, name):
                logging.error(f'Не удалось загрузить файл "{name}".')
                continue
    return True

def main():
    """
    Главная функция для запуска программы.
    """
    breed = input("Введите породу собаки: ").strip().lower()
    folder_name = input("Введите название папки для сохранения изображений на Яндекс.Диск: ").strip()

    if upload_images(breed, folder_name):
        logging.info(f'Изображения для породы "{breed}" успешно загружены в папку "{folder_name}".')
    else:
        logging.error(f'Ошибка при загрузке изображений для породы "{breed}".')


if __name__ == '__main__':
    main()