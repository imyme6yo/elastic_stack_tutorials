# @AUTHOR: imyme6yo "imyme6yo@gmail.com"
# @CREATE: 20200107
# @DESCRIPTION: Dockerfile for elastic stack container

# Args
ARG VER=19.03.5

FROM docker:${VER}

LABEL maintainer="imyme6yo"
LABEL email="imyme6yo@gmail.com"

ARG DIR=code
ARG PACKAGES=requirements.txt

RUN mkdir ${DIR}
ADD . ${DIR}
WORKDIR ${DIR}

RUN apk add --no-cache python3
RUN pip3 install --upgrade pip
RUN pip install -r ${PACKAGES}
