import time
import pytest
import requests
import os
from main import YaUploader, upload_images, get_sub_breeds

TOKEN = os.getenv('YANDEX_DISK_TOKEN')


#Тестирование функции загрузки изображений
@pytest.mark.parametrize('breed', [ 'spaniel','doberman', 'bulldog', 'collie'])
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




