import random
import pytest
import requests
import os
import logging

import retrying
from retry import retry
from retrying

#Делаем логи, для простоты отслеживания событий
logging.basicConfig(level=logging.INFO)

#Скрыть токен, для безопасности
TOKEN = os.getenv('YANDEX_DISK_TOKEN')


class YaUploader:
    def __init__(self, token):
        #Добавим основные параметры, которые будут повторяться
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
        Создаёт папку на Яндекс Диске по указанному пути.
        """

        try:
            response = requests.put(f'{self.base_url}?path={path}', headers=self.headers)
            response.raise_for_status()
            logging.info(f'Папка "{path}" успешно создана.')
        except requests.exceptions.HTTPError as err:
            logging.error(f'Ошибка при создании папки: {err}')
            return False
        return True

    #Добавим декоратор для исключения ошибок
    @retrying.retry(stop_max_attempt_number=3, wait_fixed=2000)
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

        except requests.exceptions.HTTPError as err:
            logging.error(f'Ошибка при загрузке файла "{name}": {err}')
            return False
        return True


def get_sub_breeds(breed):
    res = requests.get(f'https://dog.ceo/api/breed/{breed}/list')
    return res.json().get('message', [])


def get_urls(breed, sub_breeds):
    url_images = []
    if sub_breeds:
        for sub_breed in sub_breeds:
            res = requests.get(f"https://dog.ceo/api/breed/{breed}/{sub_breed}/images/random")
            sub_breed_urls = res.json().get('message')
            url_images.append(sub_breed_urls)
    else:
        url_images.append(requests.get(f"https://dog.ceo/api/breed/{breed}/images/random").json().get('message'))
    return url_images


def u(breed):
    sub_breeds = get_sub_breeds(breed)
    urls = get_urls(breed, sub_breeds)
    yandex_client = YaUploader()
    yandex_client.create_folder('test_folder', "AgAAAAAJtest_tokenxkUEdew")
    for url in urls:
        part_name = url.split('/')
        name = '_'.join([part_name[-2], part_name[-1]])
        yandex_client.upload_photos_to_yd("AgAAAAAJtest_tokenxkUEdew", "test_folder", url, name)


@pytest.mark.parametrize('breed', ['doberman', random.choice(['bulldog', 'collie'])])
def test_proverka_upload_dog(breed):
    u(breed)
    # проверка
    url_create = 'https://cloud-api.yandex.net/v1/disk/resources'
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': f'OAuth AgAAAAAJtest_tokenxkUEdew'}
    response = requests.get(f'{url_create}?path=/test_folder', headers=headers)
    assert response.json()['type'] == "dir"
    assert response.json()['name'] == "test_folder"
    assert True
    if get_sub_breeds(breed) == []:
        assert len(response.json()['_embedded']['items']) == 1
        for item in response.json()['_embedded']['items']:
            assert item['type'] == 'file'
            assert item['name'].startswith(breed)

    else:
        assert len(response.json()['_embedded']['items']) == len(get_sub_breeds(breed))
        for item in response.json()['_embedded']['items']:
            assert item['type'] == 'file'
            assert item['name'].startswith(breed)