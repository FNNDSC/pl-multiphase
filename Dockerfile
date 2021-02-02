# Docker file for multiphase ChRIS plugin app
#
# Build with
#
#   docker build -t <name> .
#
# For example if building a local version, you could do:
#
#   docker build -t local/pl-multiphase .
#
# In the case of a proxy (located at proxy.tch.harvard.edu:3128), do:
#
#   export PROXY=proxy.tch.harvard.edu:3138
#   docker build --build-arg http_proxy=${PROXY} --build-arg UID=$UID -t local/pl-multiphase .
#
# To run an interactive shell inside this container, do:
#
#   docker run -ti --entrypoint /bin/bash local/pl-multiphase
#
# To pass an env var HOST_IP to container, do:
#
#   docker run -ti -e HOST_IP=$(ip route | grep -v docker | awk '{if(NF==11) print $9}') --entrypoint /bin/bash local/pl-multiphase
#

FROM python:3.9.1-buster
LABEL maintainer="FNNDSC / Rudolph Pienaar <dev@babymri.org>"

WORKDIR /usr/local/src

COPY requirements.txt .
COPY "FreeSurferColorLUT.txt" /usr/src

RUN ["pip", "install", "-r", "requirements.txt"]

COPY . .
RUN ["pip", "install", "."]

WORKDIR /usr/local/bin
CMD ["multiphase", "--help"]
