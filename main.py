import django

django.setup()

from app.jobs import clear_queue, fill_queue

clear_queue.run()
