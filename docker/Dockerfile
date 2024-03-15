FROM python:3.12.0
LABEL maintainer="klimrus61@gmail.com"

ENV PYTHONUNBUFFERED 1

WORKDIR /humanRecognizer

ADD . /humanRecognizer

#COPY pyproject.toml poetry.lock ./

RUN python -m pip install --upgrade pip
RUN python -m pip install poetry
RUN poetry config virtualenvs.create false \
  && poetry lock --no-update \
  && poetry install --no-interaction --no-ansi
