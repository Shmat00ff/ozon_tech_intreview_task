import os
import time
import pytest
import requests
from main import YaUploader, upload_images, get_sub_breeds, get_urls

TOKEN = os.getenv('YANDEX_DISK_TOKEN')
TEST_BREEDS = ['bulldog', 'spaniel', 'collie', 'poodle']
TEST_INVALID_BREED = 'invalid_breed'

#Проверка работы функции get_sub_breeds
def test_get_sub_breeds():
    for breed in TEST_BREEDS:
        sub_breeds = get_sub_breeds(breed)
        assert isinstance(sub_breeds, list)
        if sub_breeds:
            assert all(isinstance(sub_breed, str) for sub_breed in sub_breeds)

    # Проверка на недопустимую породу
    invalid_sub_breeds = get_sub_breeds(TEST_INVALID_BREED)
    assert invalid_sub_breeds == []

#Проверка работы функции get_urls
def test_get_urls():
    for breed in TEST_BREEDS:
        sub_breeds = get_sub_breeds(breed)
        urls = get_urls(breed, sub_breeds)
        assert isinstance(urls, list)
        if urls:
            assert all(isinstance(url, str) and url for url in urls)

        # Проверка на количество URL
        expected_count = len(sub_breeds) if sub_breeds else 1
        assert len(urls) == expected_count

    # Проверка на недопустимую породу
    invalid_urls = get_urls(TEST_INVALID_BREED, [])
    assert invalid_urls == ['Breed not found (master breed does not exist)']

#Тестирование функции загрузки изображений
@pytest.mark.parametrize('breed', TEST_BREEDS)
def test_upload_dog(breed):
    folder_name = 'test_folder'

    yandex_client = YaUploader(TOKEN)

    assert upload_images(breed, folder_name)

    #Пауза чтобы успели все картинки прогрузиться на Диск
    time.sleep(5)

    #Проверка наличия папки на Я.Диске
    response = requests.get(f'{yandex_client.base_url}?path=/{folder_name}', headers=yandex_client.headers)
    assert response.status_code == 200
    assert response.json()['type'] == "dir"
    assert response.json()['name'] == folder_name

    #Проверка количества загруженных изображений
    items = response.json().get('_embedded', {}).get('items', [])
    sub_breeds = get_sub_breeds(breed)
    expected_count = len(sub_breeds) if sub_breeds else 1
    actual_count = sum(1 for item in items if item['name'].startswith(breed))
    assert actual_count == expected_count

    #Проверка типа файлов
    for item in items:
        if item['name'].startswith(breed):
            assert item['type'] == 'file'




