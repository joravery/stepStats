FROM python:3.10-slim-bullseye

WORKDIR /build

COPY . .

# Install updates and apt registry
RUN apt-get update -y && \
 apt-get upgrade -y && \
 apt-get dist-upgrade -y && \
 apt-get -y autoremove && \
 apt-get clean 
 
RUN apt-get install -y zip
RUN ./build.sh
