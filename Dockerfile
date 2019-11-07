FROM ubuntu:latest

RUN apt-get update && apt-get install -y python3.6 net-tools vim netcat iputils-ping

ADD main.py MessageFormats.py HelperFunctions.py ProcessVariables.py  hostfile.txt /app/
WORKDIR /app/

ENTRYPOINT ["python3.6", "main.py"]
