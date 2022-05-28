import datetime

from flask import Flask, render_template

from weather_information import current_alerts, current_observations, hourly_forecast

app = Flask(__name__)


@app.route("/")
def home():
    location = 39.14, -77.28

    forecast, city_name, utc_offset = hourly_forecast(location)
    cur_time = datetime.datetime.utcnow() - datetime.timedelta(hours=utc_offset * -1)
    threshold = 6

    new_fcst = []
    start_idx = None

    for idx, hour in enumerate(forecast):
        if start_idx and idx >= start_idx + threshold:
            break

        if int(hour["time"].split(" ")[0]) == cur_time.hour:
            start_idx = idx

        new_fcst.append(hour)

    cur_time_fmt = cur_time.strftime('%I:%M %p').lower().lstrip("0")

    all_alerts = current_alerts(location)
    icon, temp, wind_speed = current_observations(location, utc_offset)

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
        hour_6=new_fcst[5]
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


if __name__ == "__main__":
    app.run(debug=True)
