FROM ubuntu:latest

RUN apt-get update && apt-get install -y python3.6 net-tools vim netcat iputils-ping

ADD Client.py MessageFormats.py /app/
WORKDIR /app/


