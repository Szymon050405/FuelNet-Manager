import requests
from bs4 import BeautifulSoup


def get_coordinates(location_name: str) -> list[float]:

    try:
        url = f'https://pl.wikipedia.org/wiki/{location_name}'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        latitude = soup.select_one('.latitude')
        longitude = soup.select_one('.longitude')

        if latitude and longitude:
            lat = float(latitude.text.replace(',', '.'))
            lon = float(longitude.text.replace(',', '.'))
            return [lat, lon]
        else:
            raise ValueError(f"Nie znaleziono współrzędnych dla lokalizacji: {location_name}")

    except Exception as e:
        print(f"Błąd pobierania współrzędnych dla '{location_name}': {e}")
        return [52.0, 19.0]