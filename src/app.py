import datetime

from flask import Flask, render_template, request, session, redirect
import requests
from flask_session import Session

from weather_information import current_alerts, current_observations, hourly_forecast
from waitress import serve

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
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
        alert=all_alerts[page] if all_alerts else None,
        page=page,
        session_name = session["name"]
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
    return render_template(
        "critical-updates.html",
        session_name = session["name"]
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
    return render_template("reports.html",
    session_name = session["name"]
    )


if __name__ == "__main__":
    serve(
        app,
        host="0.0.0.0",
        port="8004"
    )
