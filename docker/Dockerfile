FROM python:3.6.9-alpine3.10
MAINTAINER Niall Byrne <niall@niallbyrne.ca>

ARG RUNTIME_USER=restful
ARG USER_UID=501

# Install the build-base system packages
RUN apk add --no-cache                          \
        bash                                    \
        gcc                                     \
        musl-dev                                \
        python                                  \
        python-dev

RUN mkdir -p /home/${RUNTIME_USER}/code
WORKDIR /home/${RUNTIME_USER}/code

COPY . /home/${RUNTIME_USER}/code


RUN pip3 install -r /home/${RUNTIME_USER}/code/docker/requirements-testing.txt
RUN bash /home/${RUNTIME_USER}/code/contributing/scripts/self-test.sh

RUN pip install tox
RUN tox
