import socket
from pickle import loads, dumps
from MessageFormats import ClientWriteUpdate, Client_Update

host = "container1"
PORT = 9999

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


if __name__ == '__main__':
    writing_socket = get_socket(False)
    try:
        addr = socket.gethostbyname(host)
        serv_addr = (addr, PORT)
    except socket.error as error:
        print("Error in getting address of server")
        exit(1)
    data_message = Client_Update(12,1, 1, 1, 10)
    bytes_to_send = dumps(data_message)
    num_sent = writing_socket.sendto(bytes_to_send, serv_addr)
    if num_sent < 0:
        print("No data sent")
    else:
        print("Data sent successfully to {0}".format(serv_addr))