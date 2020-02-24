FROM python:3.6-slim

RUN pip3 install pipenv
RUN apt-get update -y && apt-get install -y curl git && groupadd --gid 1000 acceptancetests && \
    useradd --create-home --system --uid 1000 --gid acceptancetests acceptancetests
WORKDIR /home/acceptancetests

COPY Pipfile* /home/acceptancetests/
RUN pipenv install --system --deploy --dev
USER acceptancetests

RUN mkdir /home/acceptancetests/.postgresql &&  mkdir /home/acceptancetests/.postgresql-rw


COPY --chown=acceptancetests . /home/acceptancetests


