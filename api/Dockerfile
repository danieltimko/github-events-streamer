FROM python:3.12-slim

WORKDIR /app
COPY . /app

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

EXPOSE 5000

RUN pip install --no-cache-dir -r requirements.txt

CMD flask run --debug
