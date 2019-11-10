FROM ubuntu:latest

RUN apt-get update && apt-get install -y python3.6 net-tools vim netcat iputils-ping

ADD main.py MessageFormats.py NetworkFunctions.py ProcessVariables.py ViewChange.py Prepare.py  hostfile.txt /app/
WORKDIR /app/

ENTRYPOINT ["python3.6", "main.py"]
