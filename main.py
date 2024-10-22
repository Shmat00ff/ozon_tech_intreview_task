import logging
import time
import requests
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv('YANDEX_DISK_TOKEN')
from dogs_api import DogsLoader
from yandex_api import YaUploader


def wait_for_file(yandex_client, path, timeout=10, interval=3):
    """
    Ожидает появления файла на Яндекс.Диске в течение указанного времени.
    """
    elapsed_time = 0
    while elapsed_time < timeout:
        response = requests.get(f'{yandex_client.base_url}?path={path}', headers=yandex_client.headers)
        if response.status_code == 200:
            return True  # Файл найден
        time.sleep(interval)
        elapsed_time += interval
    return False  # Файл не найден за отведенное время


def upload_images(breed, folder_name):
    """
    Загружает изображения для породы и ее подпород на Яндекс.Диск.
    :param breed: Название породы
    :param folder_name: Название папки для сохранения изображений.
    """
    dogs = DogsLoader()
    sub_breeds = dogs.get_sub_breeds(breed)
    urls = dogs.get_urls(breed, sub_breeds)
    yandex_client = YaUploader(TOKEN)
    #Создание папки на Я.Диске
    if not yandex_client.create_folder(folder_name):
        logging.error(f'Не удалось создать папку "{folder_name}".')
        return False

    #Загрузка изображений
    for url in urls:
        if url:
            part_name = url.split('/')
            name = part_name[-2]
            yandex_client.upload_photos_to_yd(folder_name, url, name)
            if not wait_for_file(yandex_client,f'{folder_name}/{name}'):
                logging.error(f'Не удалось загрузить файл "{name}". Новая попытка')
                yandex_client.upload_photos_to_yd(folder_name, url, name)
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