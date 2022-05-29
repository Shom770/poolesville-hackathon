import datetime
import json

import geopy
from flask import Flask, render_template, request, session, redirect
import geopy.distance
import requests
from flask_session import Session

from weather_information import current_alerts, current_observations, hourly_forecast
from waitress import serve

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

all_reports = [(0.1, (39.1881, -77.2335), 'Hail (1")', 1), (0.5, (39.1881, -77.2335), 'Sleet', 5), (0.9, (39.1881, -77.2335), 'Flooding', 19), (1, (37.1881, -77.2335), 'Sleet and Freezing Rain', 12), (1.2, (39.1881, -77.2335), 'Hail (0.25")', 21)]

REPORT_MAPPING = {
    "hail-0.25": "Hail (0.25\")",
    "hail-0.5": "Hail (0.5\")",
    "hail-0.75": "Hail (0.75\")",
    "hail-1": "Hail (1\")",
    "hail-2": "Hail (2\")",
    "hail-3": "Hail (3\")",
    "snow": "Snow",
    "sleet": "Sleet",
    "frz": "Freezing Rain",
    "snow-sleet": "Snow and Sleet",
    "sleet-frz": "Sleet and Freezing Rain",
    "graupel": "Graupel",
    "rain": "Rain",
    "drizzle": "Drizzle",
    "wind": "Windy",
    "blwngsnow": "Blowing Snow",
    "thunder": "Thunder/Lightning",
    "flood": "Flooding"
}

app.config["SECRET_KEY"] = "WxWeather1!"
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


@app.route("/")
def home():
    userip = requests.get('https://api.ipify.org').text
    response = requests.get(f"http://ip-api.com/json/{userip}").json()
    location = (response["lat"], response["lon"])

    forecast, city_name, utc_offset = hourly_forecast(location)
    cur_time = datetime.datetime.utcnow() - datetime.timedelta(hours=utc_offset * -1)
    threshold = 6

    new_fcst = forecast[1:threshold+1]
    page = int(request.args.get("page", 0))

    cur_time_fmt = cur_time.strftime('%I:%M %p').lower().lstrip("0")

    all_alerts = current_alerts(location)
    icon, temp, wind_speed = current_observations(location, utc_offset, new_fcst)

    if page < 0:
        page = 0
    elif page >= len(all_alerts):
        page = len(all_alerts) - 1

    return render_template(
        "index.html",
        date_fmt=cur_time_fmt,
        city_name=city_name,
        icon_url=icon,
        temperature=temp,
        wind_speed=wind_speed,
        hour_1=new_fcst[0],
        hour_2=new_fcst[1],
        hour_3=new_fcst[2],
        hour_4=new_fcst[3],
        hour_5=new_fcst[4],
        hour_6=new_fcst[5],
        no_alerts=bool(all_alerts),
        alert=all_alerts[page] if all_alerts else None,
        page=page,
        # session_name = session["name"]
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = {
            "username": request.form["username"],
            "password": request.form["password"]
        }
        x = requests.post("http://127.0.0.1:8001/logintosite", params=data)
        if x.text.startswith("valid:"):
            session["name"] = "wx"+str(x.text[6:])
            return redirect("/")
        else:
            return render_template("login.html")
    elif request.method == "GET":
        return render_template("login.html")

@app.route("/logout")
def logout():
    session["name"] = None
    return redirect("/")


@app.route("/criticalupdates")
def critical_updates():
    with open("static/sample.json") as file:
        sample_json = list(json.loads(file.read()).values())

    positions = [35, 35 + 11, 35 + 22, 35 + 33]
    sample_json = sorted(sample_json, key=lambda json: json["time"])[:4]


    return render_template(
        "critical-updates.html",
        json=list(zip(sample_json, positions))
        )


@app.route("/signup", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        userip = requests.get('https://api.ipify.org').text
        response = requests.get(f"http://ip-api.com/json/{userip}").json()
        location = (response["lat"], response["lon"])
        data = {
            "username": request.form["username"],
            "password": request.form["password"],
            "latitude": float(location[0]),
            "longitude": float(location[1]),
            "num_of_likes": 0,
            "num_of_posts": 0,
            "num_of_complaints": 0,
            "trust_level": "new"
        }
        x = requests.post("http://127.0.0.1:8001/adduser", params=data)
        if x.text == "User added!":
            return redirect("/login")
    elif request.method == "GET":
        return render_template("signup.html")


@app.route("/reports")
def reports():
    userip = requests.get('https://api.ipify.org').text
    response = requests.get(f"http://ip-api.com/json/{userip}").json()
    location = (response["lat"], response["lon"])

    filter_reports = []

    for report in all_reports:
        dist = round(geopy.distance.geodesic(report[1], location).miles, 2)
        filter_reports.append(
            (dist, *report[:-1], ((datetime.datetime.utcnow() - report[-1]).total_seconds() // 3600) if isinstance(report[-1], datetime.datetime) else report[-1])
        )

    filter_reports = sorted(filter_reports, key=lambda x: x[0])[:5]
    filter_reports = sorted(filter_reports, key=lambda x: x[-1])[:5]

    return render_template("reports.html", reports=filter_reports, session_name=session["name"])


@app.route("/make-a-report")
def make_a_report():
    global all_reports

    weather_type = request.args.get("type", None)
    report_type = request.args.get("report", None)

    if report_type:
        userip = requests.get('https://api.ipify.org').text
        response = requests.get(f"http://ip-api.com/json/{userip}").json()
        location = (response["lat"], response["lon"])

        all_reports.append((0, location, REPORT_MAPPING[report_type], datetime.datetime.utcnow()))

    if len(all_reports) > 100:
        all_reports = all_reports[-100:]

    return render_template("make_a_report.html", type=weather_type, session_name=session["name"])


if __name__ == "__main__":
    serve(
        app,
        host="0.0.0.0",
        port="8004"
    )
