FROM python:3.8-slim

WORKDIR /app

COPY ./flaskproject .

RUN pip install -r requirements.txt

RUN pip install earthengine-api --upgrade

ENV FLASK_APP=app.py

CMD ["flask", "run", "--host=0.0.0.0"]