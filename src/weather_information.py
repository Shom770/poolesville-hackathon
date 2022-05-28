import datetime

import requests

SESSION = requests.session()


def _gridpoints(location):
    response = SESSION.get(f"https://api.weather.gov/points/{location[0]},{location[1]}").json()["properties"]

    return response["forecastHourly"]


def hourly_forecast(location):
    """
    Format of return list:
    - List of dictionaries per hour, dictionary format is:
    {
        "time": datetime.datetime instance,
        "temperature": integer,
        "wind_speed": "[actual wind speed] mph",
        "wind_direction": "NW", "SW", etc.,
        "daytime": True or False
    """
    url = _gridpoints(location)
    filtered_json = []
    hourly_json = SESSION.get(url).json()["properties"]["periods"][:6]

    for hour in hourly_json:
        filtered_json.append({
            "time": datetime.datetime.fromisoformat(hour["startTime"]),
            "temperature": hour["temperature"],
            "wind_speed": hour["windSpeed"],
            "wind_direction": hour["windDirection"],
            "description": hour["shortForecast"],
            "daytime": hour["isDaytime"]
        })

    return filtered_json
