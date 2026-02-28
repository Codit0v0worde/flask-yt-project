FROM python:3.11.14

WORKDIR /app

ADD . /app

RUN apt-get update && apt-get install -y gcc


RUN pip install --upgrade pip setuptools

RUN pip install -r requirements.txt

CMD ["uwsgi", "app.ini"]