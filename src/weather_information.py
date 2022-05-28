import datetime

import requests
from suntime import Sun

SESSION = requests.session()


def _gridpoints(location):
    response = SESSION.get(f"https://api.weather.gov/points/{location[0]},{location[1]}").json()["properties"]

    return response["forecastHourly"]


def hourly_forecast(location, go_out=6):
    """
    Format of return list:
    - List of dictionaries per hour, dictionary format is:
    {
        "time": datetime.datetime instance,
        "temperature": integer,
        "wind_speed": "[actual wind speed] mph",
        "wind_direction": "NW", "SW", etc.,
        "daytime": True or False,
        "icon": relative url to icon eg "static/cloudy.png"
    }
    """
    url = _gridpoints(location)
    filtered_json = []
    hourly_json = SESSION.get(url).json()["properties"]["periods"][:go_out]
    sun = Sun(*location)

    for idx, hour in enumerate(hourly_json):
        time = datetime.datetime.fromisoformat(hour["startTime"])
        forecast = hour["shortForecast"].lower()
        utc_offset = int(time.utcoffset().total_seconds() // 3600)

        sunrise = sun.get_sunrise_time(time) - datetime.timedelta(hours=utc_offset * -1)
        sunset = sun.get_sunset_time(time) - datetime.timedelta(hours=utc_offset * -1)

        daytime = sunrise.hour <= time.hour <= sunset.hour

        if 'mostly clear' in forecast or 'mostly sunny' in forecast:
            if daytime:
                icon = "static/mostly_clear.png"
            else:
                icon = "static/night_mostly_cloudy.png"
        elif forecast in ('partly cloudy', 'partly sunny', 'mostly cloudy'):
            if daytime:
                icon = "static/partly_cloudy.png"
            else:
                icon = "static/night_mostly_cloudy.png"
        elif 'haze' in forecast or 'fog' in forecast:
            icon = "static/haze.png"
        elif "cloudy" in forecast:
            if daytime:
                icon = "static/cloudy.png"
            else:
                icon = "static/night_mostly_cloudy.png"
        elif forecast == "sunny":
            icon = "static/sunny.png"
        elif forecast == "clear":
            icon = "static/clear.png"
        elif 'thunderstorm' in forecast:
            icon = "static/thunderstorms.png"
        elif 'rain' in forecast or 'showers' in forecast:
            icon = "static/rain.png"
        elif 'freezing rain' in forecast:
            icon = "static/frz_rain.png"
        elif 'sleet' in forecast:
            icon = "static/sleet.png"
        elif 'snow' in forecast:
            icon = "static/snowy.png"

        filtered_json.append({
            "time": datetime.datetime.fromisoformat(hour["startTime"]),
            "temperature": hour["temperature"],
            "wind_speed": hour["windSpeed"],
            "wind_direction": hour["windDirection"],
            "description": forecast,
            "daytime": daytime,
            "icon": icon
        })

    return filtered_json


def current_alerts(location, include_text=False):
    """
    Spec of json:
    {
        "start_time": datetime.datetime instance,
        "end_time": datetime.datetime instance,
        "name": Name of event (like Winter Storm Warning),
        "event_text": Whole event text, including hazards, direction of storm if it's a severe storm, etc.
        (only includes text if include_text is True)
    }
    """
    alerts_json = SESSION.get(
        f"https://api.weather.gov/alerts/active",
        params={"point": f"{location[0]},{location[1]}"}
    ).json()["features"]
    filtered_json = []

    for alert in alerts_json:
        alert_prop = alert["properties"]
        filtered_json.append({
            "start_time": datetime.datetime.fromisoformat(alert_prop["onset"]),
            "end_time": datetime.datetime.fromisoformat(alert_prop["expires"]),
            "name": alert_prop["event"],
            "event_text": alert_prop["description"] if include_text else None
        })

    return filtered_json
