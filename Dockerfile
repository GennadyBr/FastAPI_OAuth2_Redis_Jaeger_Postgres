FROM python:3.11

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt

RUN  pip3 install --no-cache-dir --upgrade pip \
     && pip3 install --no-cache-dir -r requirements.txt

COPY /src .
COPY gunicorn.conf.py gunicorn.conf.py

EXPOSE 8081

CMD ["gunicorn",  "main:app", "-c", "gunicorn.conf.py"]