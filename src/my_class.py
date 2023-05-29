import requests
import json

class NASA:

    def __init__(self, start_date, api_key, end_date=None):
        self.base_url = 'https://api.nasa.gov/'
        self.start_date = start_date
        self.end_date = end_date
        self.api_key = api_key

    def get_asteroids(self):
        url = self.base_url + f'neo/rest/v1/feed?start_date={self.start_date}&end_date={self.end_date}&api_key={self.api_key}'
        r = requests.get(url)
        data = json.loads(r.text)
        return data

    def get_hazardous_asteroids(self):
        url = self.base_url + f'neo/rest/v1/feed?start_date={self.start_date}&end_date={self.end_date}&api_key={self.api_key}'
        r = requests.get(url)
        data = r.json()
        neo = data['near_earth_objects']
        hazardous_asteroids = []
        for date in neo:
            for near in neo[date]:
                if near['is_potentially_hazardous_asteroid']:
                    asteroid_info = {
                        'ID астероида': near['id'],
                        'Имя': near['name'],
                        'Предполагаемый диаметр': near["estimated_diameter"]["kilometers"]["estimated_diameter_max"],
                        'Потенциальная опасность': near['is_potentially_hazardous_asteroid']
                        }
                    hazardous_asteroids.append(asteroid_info)
        return hazardous_asteroids

    def get_apod(self):
        url_apod = self.base_url + 'planetary/apod'
        params = {
            'api_key': self.api_key,
            'date': self.start_date
        }
        try:
            response = requests.get(
                url_apod, params=params
            )
            data = response.json()
            return data

        except Exception as ex:
            print(ex)
            return 'Проверьте корректность введенных данных'

    def get_epic(self):
        url_epic = self.base_url + 'EPIC/api/natural/date/' + self.start_date
        params = {
            'api_key': self.api_key,
        }
        try:
            response = requests.get(
                url_epic, params=params
            )
            data = response.json()
            return data

        except Exception as ex:
            print(ex)
            return 'Проверьте корректность введенных данных'
