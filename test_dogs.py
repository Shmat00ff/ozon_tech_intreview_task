import pytest
import requests
import os
from dogs_api import DogsLoader
from yandex_api import YaUploader
from main import upload_images
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv('YANDEX_DISK_TOKEN')
TEST_BREEDS = ['bulldog', 'spaniel', 'collie', 'poodle', 'doberman']
TEST_INVALID_BREED = 'invalid_breed'
dogs = DogsLoader()
TEST_FOLDER_NAME = 'test_folder_1'


@pytest.fixture(scope='session')
def yandex_client():
    """
    Создаем клиента для работы с Яндекс.Диском, который будет использоваться в тестах.
    """
    client = YaUploader(TOKEN)
    yield client
    # Очистка после завершения всех тестов
    response = requests.delete(f'{client.base_url}?path={TEST_FOLDER_NAME}&permanently=true', headers=client.headers)
    if response.status_code == 202:
        print(f'Папка "{TEST_FOLDER_NAME}" успешно удалена после тестов.')
    else:
        print(f'Не удалось удалить папку "{TEST_FOLDER_NAME}" после тестов. Статус: {response.status_code}')


#Тестирование функции загрузки изображений
@pytest.mark.parametrize('breed', TEST_BREEDS)
def test_upload_dog(breed, yandex_client):
    folder_name = TEST_FOLDER_NAME

    assert upload_images(breed, folder_name)


    #Проверка наличия папки на Я.Диске
    response = requests.get(f'{yandex_client.base_url}?path=/{folder_name}', headers=yandex_client.headers)
    assert response.status_code == 200
    assert response.json()['type'] == "dir"
    assert response.json()['name'] == folder_name

    #Проверка количества загруженных изображений
    items = response.json().get('_embedded', {}).get('items', [])
    sub_breeds = dogs.get_sub_breeds(breed)
    expected_count = len(sub_breeds) if sub_breeds else 1
    actual_count = sum(1 for item in items if item['name'].startswith(breed))
    assert actual_count == expected_count

    #Проверка типа файлов
    for item in items:
        if item['name'].startswith(breed):
            assert item['type'] == 'file'




