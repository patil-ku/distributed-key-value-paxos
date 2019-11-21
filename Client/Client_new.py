from cmd import Cmd


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


def write_data(data,reciever):
    writing_socket = get_socket(False)
    try:
        addr = socket.gethostbyname(host)
        serv_addr = (addr, PORT)
    except socket.error as error:
        print("Error in getting address of server")
        exit(1)
    #type,client_id,server_id,timestamp,update
    data_message = Client_Update(12,1, reciever,1,data)
    bytes_to_send = dumps(data_message)
    num_sent = writing_socket.sendto(bytes_to_send, serv_addr)
    if num_sent < 0:
        #print("No data sent")
        return "Error in writing data"

    else:
        s = "Data sent successfully to"+str(serv_addr)
        return s
        #print("Data sent successfully to {0}".format(serv_addr))


def read_data(data):
    #have to figure out, after doing k_v store

 
class MyPrompt(Cmd):

    def do_GET(self, data):
    	if(data):
    		print("data to be fetched is ",data)
            read_data(data)

    	else:
    		print("data not found for reading ")

    def do_POST(self,data):
    	if(data):
            update,reciever = data.split()
            #print("data to be write ",data)
            #for now it accepts numeric server id's as receiver value
            status = write_data(update,reciever)
            print(status)
    		
    	else:
    		print("data not found for writing ")

    
    def do_EOF(self, line):
        return True



if __name__ == '__main__':
    MyPrompt().cmdloop()