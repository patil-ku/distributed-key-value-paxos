# Distributed Key Value Store 

This project implements a distributed key value store that is consistent, available and fault tolerant.
The Key-Value store uses the Paxos algorithm at its heart for consensus and all the above mentioned features.


## Motivation

To address the audiences with modern web and to handle large amounts of data, many applications are taking the distributed systems approach. However this comes with its own set of problems such as data availability, data accuracy and minimized cost of overheads for doing basic reads and writes. The most intuitive way to approach this is by using key-value stores, since they are simple and speedy. The path to retrieve data is a direct request to the object in memory or on disk. The relationship between data does not have to be calculated by a query language; there is no optimization performed. They can exist on distributed systems and don’t need to worry about where to store indexes, how much data exists on each system or the speed of a network within a distributed system they just work.
With this project, we aim at building our own implementation of a distributed key-value store. With each distributed system, comes the problem of having consensus in the system, that is, having each server agree on a particular update; this in turn provides the consistency which is highly desired in any system. To overcome this problem, we plan to implement our key-value store over an implementation of the replicated paxos protocol. By using Paxos we can be sure that we will achieve strong consistency, fault-tolerance as well as high availability. 
We are mainly focused on keeping the data consistent and available since these properties are majorly required in application scenarios like bank, military, health,etc. For these applications, any inconsistency in replicas is intolerable. In such situations, when exposed to hostile system environments, two-phase commits may not guarantee strong consistency among multiple replicas and high system availability. With three or more replicas, the Paxos family of protocols is considered to be the only solution to guarantee the strong replication consistency. High availability is also a very desirable property for systems that provide 24x7 reliable services. 



## Tech Used

Python3.6
Docker
Protobuffs


## Structure of code

 - The client code is available in the Client folder. 
 - The server code is placed in the Paxos_Servers folder. This includes all the paxos phases separated in different python files.
 - Currently, the system supports 5 servers named : container0 - container4, which has been defined in the hostfile.txt
 - If needed more server names could be added to the hostfile.


## Building and running code

 - To run this project you will need to have docker installed. 
 - Please ensure that you have a docker bridge network installed for the servers to connect on.
 - To install a docker network, run:

 ``` bash
 docker network create paxos_network
 ```

### Running the Client:

 - This should be run separately on different docker instances.
 - To build and run the client, navigate to the Client folder, open a terminal here and run :

 ``` bash
 docker build . -t paxos_client

 docker run --network paxos_network --name client1 --rm -ti paxos_client
```

### Running the Servers:

 - There are bash scripts available to build and run the servers.
 - To build the docker image, you can just run:

 ``` bash
 ./remove_and_build
 ```
 - This will check if there are any containers of names container0 - container4 running, remove them and then build a new image
 - Or, you can build using:

 ``` bash
 docker build . -t paxos
 ```

 - To run the servers, there is a bash script available that will startup all the servers in different terminals:

 ``` bash
 ./run_all_servers
 ```

 - You can also run each server individualy by opening a separate terminal for each server and running the following commands:
 ``` bash
 docker run --rm -ti  --name container0 --network first_network paxos -h hostfile.txt -n container0
 docker run --rm -ti  --name container1 --network first_network paxos -h hostfile.txt -n container1
 docker run --rm -ti  --name container2 --network first_network paxos -h hostfile.txt -n container2
 docker run --rm -ti  --name container3 --network first_network paxos -h hostfile.txt -n container3
 docker run --rm -ti  --name container4 --network first_network paxos -h hostfile.txt -n container4
 ```

 - The parameters required are "-h" for the hostfile.txt containing all the server names and "-n" specifying the container's own name.


## How to Use

 - Once you have started up the servers and the servers read the following message "All Nodes are up!"; the client can then start sending requests
 - On the client side, there are four 4 apis provided for interacting with the key-value store

```
 	1. set <key> <value> : This is used to save/write data to the key-value store. 
 	2. get <key>		 : This is used to retrieve the value for a key
 	3. iset <image location> <metadata> : iset is used for saving image hashes and their related metadata. You need to provide the location of the image and its metadata
 	4. iget <image location> : This is used to retrieve the given image's metadata.
```