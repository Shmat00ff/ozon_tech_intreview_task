import logging
import requests

class DogsLoader:
    """
    Класс для работы с DOGS API.
    """
    def __init__(self):
        self.base_url = 'https://dog.ceo/api/breed/'

    def get_sub_breeds(self, breed):
        """
        Получает список подпород для указанной породы.
        :param breed: Название породы.
        :return: Список подпород к данной породе.
        """
        try:
            response = requests.get(f'{self.base_url}{breed}/list')
            response.raise_for_status()
            return response.json().get('message', [])
        except (requests.exceptions.HTTPError, ValueError) as err:
            logging.error(f'Ошибка при получении подпород для "{breed}": {err}')
            return []



    def get_urls(self, breed: str, sub_breeds: list):
        """
        Получает список URL случайных изображений для породы и ее подпород.
        :param breed: Название породы.
        :param sub_breeds: Список подпород к данной породе.
        :return: Список ссылок на изображения
        """
        url_images = []
        if sub_breeds:
            for sub_breed in sub_breeds:
                res = requests.get(f"{self.base_url}{breed}/{sub_breed}/images/random")
                sub_breed_urls = res.json().get('message')
                url_images.append(sub_breed_urls)
        else:
            url_images.append(requests.get(f"{self.base_url}{breed}/images/random").json().get('message'))
        return url_images

