import django

django.setup()

from app.jobs import main

main.run()
