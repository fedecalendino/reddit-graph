from time import sleep
from threading import Thread
import requests
from flask import Flask


# Flask =========================================================================
app = Flask(__name__)


@app.route("/heartbeat")
def hello():
    return "🌿 Yahaha! You found me! 🌿"


@app.before_first_request
def activate_job():
    def run_job():
        import django

        django.setup()

        import app.jobs.main

        app.jobs.main.run()

    run_job_thread = Thread(target=run_job)
    run_job_thread.start()


def start_runner():
    def start_loop():
        not_started = True

        while not_started:
            print('Checking if server is alive...')

            try:
                r = requests.get(f'http://{IP}:{PORT}/heartbeat')

                if r.status_code == 200:
                    print('Server started...')
                    not_started = False

                print(r.status_code)
            except:
                print('Server not yet started...')

            sleep(1)

    print('Started runner')
    start_loop_thread = Thread(target=start_loop)
    start_loop_thread.start()


# Main ========================================================================

import os

PORT = int(os.environ.get('PORT', 5000))
IP = '127.0.0.1' if PORT == 5000 else '0.0.0.0'


if __name__ == "__main__":
    start_runner()

    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host=IP, port=PORT)