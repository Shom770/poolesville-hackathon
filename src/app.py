import datetime
import socket

import requests
from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import SelectField

from weather_information import current_alerts, current_observations, hourly_forecast

app = Flask(__name__)


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
    icon, temp, wind_speed = current_observations(location, utc_offset)

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
        alert=all_alerts[page] if bool(all_alerts) else None,
        page=page
    )


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/criticalupdates")
def critical_updates():
    return render_template("critical-updates.html")


@app.route("/signup")
def sign_up():
    return render_template("signup.html")


@app.route("/reports")
def reports():
    return render_template("reports.html")


@app.route("/make-a-report")
def make_a_report():
    return render_template("make_a_report.html")


if __name__ == "__main__":
    app.run(debug=True)
