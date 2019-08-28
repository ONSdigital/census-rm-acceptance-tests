FROM python:3.6-slim

RUN pip3 install pipenv
RUN apt-get update -y && apt-get install -y curl git
WORKDIR /app
COPY . /app
RUN pipenv install --system --deploy --dev