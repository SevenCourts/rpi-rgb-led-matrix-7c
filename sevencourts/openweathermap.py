"""
Openweathermap integration
"""

import requests
import sevencourts.logging as logging

_log = logging.logger("openweathermap")

## TODO check https://openweathermap.org/price#weather

# API key from OpenWeatherMap
# FIXME pass the API_KEY via environment
API_KEY = "c462c344b198f6b837de800561227e2e"

# The base URL for the OpenWeatherMap API.
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"


def fetch_weather(city: str):
    try:
        # 'units=metric' gives the temperature in Celsius.
        params = {"appid": API_KEY, "q": city, "units": "metric"}
        response = requests.get(BASE_URL, params=params, timeout=10)
        if response.status_code == 200:
            # Parse the JSON data from the response.
            data = response.json()

            # Extract the main weather information.
            main_data = data.get("main", {})
            temperature = int(main_data.get("temp"))
            humidity = main_data.get("humidity")

            # Extract rain information, if available.
            # The 'rain' key may not exist if there is no rain.
            rain_data = data.get("rain", {})
            rain_volume = rain_data.get(
                "1h", "No rain data"
            )  # Rain volume in the last 1 hour.

            # Get the weather description for a more detailed report.
            weather_description = data.get("weather", [{}])[0].get(
                "description", "Not available"
            )

            return {
                "city": city,
                "temperature": temperature,
                "humidity": humidity,
                "rain_volume": rain_volume,
                "weather_description": weather_description.capitalize(),
            }
        else:
            _log.error(
                f"Error fetching weather data. Status code: {response.status_code}"
            )
            _log.debug(response.json())
    except requests.exceptions.RequestException as ex:
        _log.error(f"An error occurred: {ex}")
        _log.debug(f"An error occurred: {ex}", ex)


# Main function
if __name__ == "__main__":
    import sys

    weather = fetch_weather(sys.argv[1] if len(sys.argv) > 1 else "Böblingen,DE")
    print(weather)
    if weather:
        print(f"Weather in {weather.get('city')}:")
        print(f"----------------------")
        print(f"Temperature: {weather.get('temperature')}°C")
        print(f"Humidity: {weather.get('humidity')}%")
        print(f"Rain (last 1h): {weather.get('rain_volume')} mm")
        print(f"Description: {weather.get('weather_description').capitalize()}")
