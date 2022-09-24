import django
django.setup()

import app.jobs.main
app.jobs.main.run()
