FROM python:3.9.5-slim

WORKDIR /app

RUN apt update
RUN apt install -y curl git libpq-dev postgresql-client
RUN psql --version


RUN git config --global user.email "fede@calendino.com"
RUN git config --global user.name "Fede Calendino"


COPY requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt


COPY app /app/app
COPY release /app/release
COPY main.py /app/main.py
COPY manage.py /app/manage.py
COPY settings.py /app/settings.py

RUN chmod +x /app/release/make.sh

EXPOSE 8000:8000
ENV DJANGO_SETTINGS_MODULE=settings
ENV PYTHONUNBUFFERED=1


CMD python3 -m flask --app main run --host 0.0.0.0 --port 8000
