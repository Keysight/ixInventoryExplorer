# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /python-docker
RUN apt-get update && apt-get install -y procps && rm -rf /var/lib/apt/lists/*
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
ENV PIP_ROOT_USER_ACTION=ignore
RUN pip3 install --upgrade pip
RUN pip3 install setuptools
COPY . .
EXPOSE 3000


CMD ["/bin/sh", "runApplication.sh"]



