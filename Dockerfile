# pull official base image
FROM python:3.11.4-alpine

ARG APP_HOME=/app
ARG APP_PORT=8000

# set work directory
WORKDIR $APP_HOME

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
# RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

RUN mkdir static
RUN mkdir ./static/staticfiles
RUN mkdir ./static/mediafiles

# copy project
COPY . .

EXPOSE $APP_PORT