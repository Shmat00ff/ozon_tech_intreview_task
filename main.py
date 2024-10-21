import logging
import os
from dogs_api import DogsLoader
from image_loader import YaUploader
TOKEN = os.getenv('YANDEX_DISK_TOKEN')

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