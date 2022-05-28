from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def home():
    location = 39.14, -77.28

    return render_template("index.html")


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
