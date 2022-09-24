from threading import Thread

from flask import Flask


def run_main_job():
    import django

    django.setup()

    import app.jobs.main

    app.jobs.main.run()


def create_app(test_config=None):
    app = Flask(
        __name__,
        instance_relative_config=True,
    )

    run_job_thread = Thread(target=run_main_job)
    run_job_thread.start()

    @app.route("/")
    def hello():
        return "🌿 Yahaha! You found me! 🌿"

    app.run(host="0.0.0.0", port=8000)
    return app
