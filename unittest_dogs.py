from dogs_api import DogsLoader
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv('YANDEX_DISK_TOKEN')
TEST_BREEDS = ['bulldog', 'spaniel', 'collie', 'poodle']
TEST_INVALID_BREED = 'invalid_breed'
dogs = DogsLoader()

#Проверка работы функции get_sub_breeds
def test_get_sub_breeds():
    for breed in TEST_BREEDS:
        sub_breeds = dogs.get_sub_breeds(breed)
        assert isinstance(sub_breeds, list)
        if sub_breeds:
            assert all(isinstance(sub_breed, str) for sub_breed in sub_breeds)

    # Проверка на недопустимую породу
    invalid_sub_breeds = dogs.get_sub_breeds(TEST_INVALID_BREED)
    assert invalid_sub_breeds == []

#Проверка работы функции get_urls
def test_get_urls():
    for breed in TEST_BREEDS:
        sub_breeds = dogs.get_sub_breeds(breed)
        urls = dogs.get_urls(breed, sub_breeds)
        assert isinstance(urls, list)
        if urls:
            assert all(isinstance(url, str) and url for url in urls)

        # Проверка на количество URL
        expected_count = len(sub_breeds) if sub_breeds else 1
        assert len(urls) == expected_count

    # Проверка на недопустимую породу
    invalid_urls = dogs.get_urls(TEST_INVALID_BREED, [])
    assert invalid_urls == ['Breed not found (master breed does not exist)']