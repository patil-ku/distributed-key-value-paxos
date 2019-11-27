import argparse
import socket
from pickle import loads, dumps

from MessageFormats import ClientWriteUpdate, Client_Update
import select
import sys


PORT = 9999
BUFFER_SIZE = 1024


class ClientProcessVariables:
    def __init__(self):
        self.timestamp = 0
        self.pid = 99 # Random for now, will have to change later
        self.connected_server_id = -1
        self.connected_server = None


def get_socket(bindStatus):
    try:
        sockfd = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        # print("SOCKET")
        # print(sockfd)
    except socket.error as msg:
        print("Error while calling socket:: " + msg)
        socket.close(sockfd)
    if bindStatus:
        try:
            sockfd.bind(('', PORT))
            # print("Binded listening socket!")
        except socket.error as msg:
            print("Error in binding:: " + msg)
            socket.close(sockfd)
    sockfd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)
    sockfd.setblocking(0)
    return sockfd


# More processing for types of user inputs here, for the time being this just handles WRITE
# On WRITE, this will form a client_update message with the value passed later on.
def process_user_input(line, my_info):

    commands = line.split(' ')
    if commands[0] == 'WRITE':
        print("Sending data {0} to {1}".format(commands[1], my_info.connected_server_id))
        data_to_be_sent = commands[1] + " " + commands[2]
        write_data(data_to_be_sent, my_info)

    if commands[0] == 'READ':
        print("Reads not supported yet")

    if commands[0] != 'READ' and commands[0] != 'WRITE':
        print("Not supported yet")


def write_data(data_to_be_sent, my_info):
    writing_socket = get_socket(False)
    try:
        addr = socket.gethostbyname(my_info.connected_server)
        serv_addr = (addr, PORT)
    except socket.error as error:
        print("Error in getting address of server")
        exit(1)
    my_info.timestamp += 1
    data_message = Client_Update(12, my_info.pid, my_info.connected_server_id, my_info.timestamp, data_to_be_sent)
    bytes_to_send = dumps(data_message)
    num_sent = writing_socket.sendto(bytes_to_send, serv_addr)
    if num_sent < 0:
        print("No data sent")
    else:
        print("Data sent successfully to {0}".format(serv_addr))


if __name__ == '__main__':
    # Create a command line parser
    parser = argparse.ArgumentParser(description='Get current container name to connect to, ', add_help=False)
    # Add the arguments to be handled
    parser.add_argument('-h', type=str)
    # -p for process id of client
    parser.add_argument('-p', type=str)
    args = parser.parse_args()
    host = args.h
    pid = args.p

    connected_server_id = int(host.split('r')[1])
    my_info = ClientProcessVariables()
    my_info.connected_server_id = connected_server_id
    my_info.pid = pid
    my_info.connected_server = host
    listening_socket = get_socket(True)
    inputs = [listening_socket, sys.stdin]
    while True:
        readable, writable, _ = select.select(inputs, [], [])

        for s in readable:
            if s is listening_socket:
                print("Got something from the server")
                msg, address = s.recvfrom(BUFFER_SIZE)
                recvd_msg = loads(msg)
                # For now the server only sends a string
                print(recvd_msg)

            if s is sys.stdin:
                print("User entered something:")
                line = sys.stdin.readline().rstrip()
                process_user_input(line, my_info)
