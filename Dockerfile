FROM python:3.9.5-slim

WORKDIR /app

RUN apt update
RUN apt install -y curl git postgresql-client
RUN psql --version

COPY requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt

COPY app /app/app
COPY main.py /app/main.py
COPY manage.py /app/manage.py
COPY settings.py /app/settings.py

ENV DJANGO_SETTINGS_MODULE=settings
ENV PYTHONUNBUFFERED=1

CMD ["python3", "/app/main.py"]
