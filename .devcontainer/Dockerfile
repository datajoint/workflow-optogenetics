FROM mcr.microsoft.com/devcontainers/python:3.7-bullseye

RUN \
    # dev setup
    apt update && \
    apt-get install bash-completion graphviz default-mysql-client -y && \
    pip install --no-cache-dir --upgrade black pip

COPY ./requirements.txt /tmp/
RUN \
    # workflow dependencies
    pip install --no-cache-dir -r /tmp/requirements.txt && \
    # clean up
    rm /tmp/requirements.txt && \
    apt-get clean

ENV DJ_HOST fakeservices.datajoint.io
ENV DJ_USER root
ENV DJ_PASS simple

ENV DATABASE_PREFIX neuro_