FROM python:3.10-slim-buster
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /usr/bin/authapp
COPY ./requirements.txt /usr/bin/authapp
RUN pip install -r requirements.txt
COPY . .
