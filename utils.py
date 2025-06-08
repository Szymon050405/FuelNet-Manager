import requests

def get_city_coordinates(city_name: str) -> list:

    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": city_name,
            "format": "json",
            "limit": 1
        }
        headers = {
            "User-Agent": "fuelnet-app"
        }

        res = requests.get(url, params=params, headers=headers)
        data = res.json()

        if data:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            return [lat, lon]
        else:
            raise ValueError("Nie znaleziono miasta")

    except Exception as e:
        print(f"Błąd geolokalizacji '{city_name}': {e}")
        return [52.0, 19.0]


def get_fuel_stations_near_city(city_name: str) -> list:

    try:
        lat, lon = get_city_coordinates(city_name)

        overpass_url = "https://overpass-api.de/api/interpreter"
        query = f"""
        [out:json];
        node
          ["amenity"="fuel"]
          (around:5000,{lat},{lon});
        out;
        """

        res = requests.post(overpass_url, data=query.encode('utf-8'))
        data = res.json()

        stations = []
        for element in data["elements"]:
            name = element["tags"].get("name", "Stacja bez nazwy")
            stations.append({
                "name": name,
                "lat": element["lat"],
                "lon": element["lon"]
            })

        return stations

    except Exception as e:
        print(f"Błąd pobierania stacji dla '{city_name}': {e}")
        return []