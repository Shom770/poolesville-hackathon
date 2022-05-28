# import random
# import re
# import sys
# import threading
# import time
# from flask import Flask, render_template
# from turbo_flask import Turbo
#
# app = Flask(__name__)
# turbo = Turbo(app)
#
#
# @app.context_processor
# def inject_load():
#     if sys.platform.startswith('linux'):
#         with open('/proc/loadavg', 'rt') as f:
#             load = f.read().split()[0:3]
#     else:
#         load = [int(random.random() * 100) / 100 for _ in range(3)]
#     return {'load1': load[0], 'load5': load[1], 'load15': load[2]}
#
#
# @app.route('/')
# def index():
#     return render_template('index.html')
#
#
# @app.route('/page2')
# def page2():
#     return render_template('page2.html')
#
#
# @app.before_first_request
# def before_first_request():
#     threading.Thread(target=update_load).start()
#
#
# def update_load():
#     with app.app_context():
#         while True:
#             time.sleep(5)
#             turbo.push(turbo.replace(render_template('loadavg.html'), 'load'))

from flask import Flask, jsonify
from flask_simple_geoip import SimpleGeoIP


app = Flask(__name__)

# The API key is obtained from the GEOIPIFY_API_KEY environment variable.
# Alternatively it can be set as follows:
app.config.update(GEOIPIFY_API_KEY='YOUR_API_KEY')

# Initialize the extension
simple_geoip = SimpleGeoIP(app)


@app.route('/')
def test():
    # Retrieve geoip data for the given requester
    geoip_data = simple_geoip.get_geoip_data()

    return jsonify(data=geoip_data)