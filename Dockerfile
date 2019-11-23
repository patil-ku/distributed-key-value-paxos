FROM ubuntu:latest

RUN apt-get update && apt-get install -y python3.6 net-tools vim netcat iputils-ping

ADD main.py MessageFormats.py NetworkFunctions.py ProcessVariables.py ViewChange.py Prepare.py  hostfile.txt FileOps.py ClientFuntions.py Proposal.py Accept.py  ClientUpdateExecution.py Recovery.py run_server  /app/



WORKDIR /app/

RUN chmod u+x run_server


ENTRYPOINT ["python3.6", "main.py"]

