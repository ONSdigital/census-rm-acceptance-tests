FROM python:3.6-slim

WORKDIR /app
COPY . /app
RUN apt-get update -y && apt-get install -y python-pip && apt-get install -y curl && apt-get install -y git
RUN pip3 install pipenv && pipenv install --system --deploy --dev
