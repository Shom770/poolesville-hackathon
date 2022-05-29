import datetime

import requests
from suntime import Sun

SESSION = requests.session()


def _gridpoints(location, type_="forecastHourly"):
    response = SESSION.get(f"https://api.weather.gov/points/{location[0]},{location[1]}").json()["properties"]
    location = response["relativeLocation"]["properties"]

    return response[type_], f"{location['city']}, {location['state']}"


def current_observations(location, utc_offset):
    url, loc = _gridpoints(location, "observationStations")
    url = SESSION.get(url).json()["features"][0]["id"]
    response = SESSION.get(url + "/observations/latest").json()["properties"]
    sun = Sun(*location)

    time = datetime.datetime.fromisoformat(response["timestamp"])
    time -= datetime.timedelta(hours=utc_offset * -1)

    text_desc = response["textDescription"].lower()
    sunrise = sun.get_sunrise_time(time) - datetime.timedelta(hours=utc_offset * -1)
    sunset = sun.get_sunset_time(time) - datetime.timedelta(hours=utc_offset * -1)

    daytime = sunrise.hour <= time.hour <= sunset.hour

    if 'mostly clear' in text_desc or 'mostly sunny' in text_desc:
        if daytime:
            icon = "static/mostly_clear.png"
        else:
            icon = "static/night_mostly_cloudy.png"
    elif text_desc in ('partly cloudy', 'partly sunny', 'mostly cloudy'):
        if daytime:
            icon = "static/partly_cloudy.png"
        else:
            icon = "static/night_mostly_cloudy.png"
    elif 'haze' in text_desc or 'fog' in text_desc:
        icon = "static/haze.png"
    elif "cloudy" in text_desc:
        if daytime:
            icon = "static/cloudy.png"
        else:
            icon = "static/night_mostly_cloudy.png"
    elif "sunny" in text_desc:
        icon = "static/sunny.png"
    elif "clear" in text_desc:
        if daytime:
            icon = "static/sunny.png"
        else:
            icon = "static/night_clear.png"
    elif 'thunderstorm' in text_desc:
        icon = "static/thunderstorms.png"
    elif 'rain' in text_desc or 'showers' in text_desc:
        icon = "static/rain.png"
    elif 'freezing rain' in text_desc:
        icon = "static/frz_rain.png"
    elif 'sleet' in text_desc:
        icon = "static/sleet.png"
    elif 'snow' in text_desc:
        icon = "static/snowy.png"

    if response["temperature"]["value"] is None:
        temp = 0
    else:
        temp = response["temperature"]["value"]

    if response["windSpeed"]["value"] is None:
        ws = 0
    else:
        ws = response["temperature"]["value"]

    temperature = (temp * (9 / 5)) + 32  # Convert celsius to fahrenheit
    wind_speed = (ws / 1.609344)  # Convert km/h to mph

    return icon, round(temperature), round(wind_speed)


def hourly_forecast(location, go_out=24):
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
    url, loc = _gridpoints(location)
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
            if daytime:
                icon = "static/sunny.png"
            else:
                icon = "static/night_clear.png"

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
            "time": datetime.datetime.fromisoformat(hour["startTime"]).strftime('%I %p').lower().lstrip("0"),
            "temperature": hour["temperature"],
            "wind_speed": hour["windSpeed"],
            "wind_direction": hour["windDirection"],
            "description": forecast,
            "daytime": daytime,
            "icon": icon
        })

    return filtered_json, loc, utc_offset


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
        if alert_prop["onset"] is None:
            continue

        start_time = datetime.datetime.fromisoformat(
            alert_prop["onset"]
        )
        end_time = datetime.datetime.fromisoformat(
            alert_prop["expires"]
        )
        start, end = min((start_time, end_time)), max(start_time, end_time)

        filtered_json.append({
            "start_time": start.strftime('%I:%M %p (%m/%d/%Y)').lower().lstrip("0"),
            "end_time": end.strftime('%I:%M %p (%m/%d/%Y)').lower().lstrip("0"),
            "name": alert_prop["event"],
            "severity": alert_prop["severity"],
            "certainty": alert_prop["certainty"],
            "event_text": alert_prop["description"] if include_text else None
        })

    return filtered_json
