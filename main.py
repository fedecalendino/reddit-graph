import django

django.setup()

from app.jobs import check

check.run("hearthstone")
