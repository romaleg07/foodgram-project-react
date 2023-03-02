FROM python:3.10.6-slim

LABEL author="Romaleg" version=1

WORKDIR /app

COPY requirements.txt /app

RUN apt-get update && apt-get upgrade -y && \
    pip install --upgrade pip && pip install -r /app/requirements.txt

COPY . .

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0.0.0.0:8000" ]