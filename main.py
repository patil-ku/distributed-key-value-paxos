# Import statements
import socket
import argparse
import select
from pickle import loads, dumps
import queue

from HelperFunctions import are_all_nodes_up, send_to_all_servers, get_socket
from MessageFormats import AliveAckMessage, AliveMessage, Message, VC_Proof, View_Change
import time
import threading
from ProcessVariables import ProcessVariables, LEADER_ELECTION, REG_NON_LEADER, REG_LEADER
from random import seed, randint

# Constants defined here
PORT = 9999
LOCAL_ADDRESS = "127.0.0.1"
BUFFER_SIZE = 1024


def timer_thread(sleep_time):
    # print("Starting:: {0} Progress_Timer: {1}".format(threading.current_thread().getName(), sleep_time))
    time.sleep(sleep_time)
    # print("Exiting:: {0}".format(threading.current_thread().getName()))


# Thread function to send VC_Proof messages every 5 seconds (Hopefully)
def thread_send_vc_proof(my_info, last_installed_queue, last_installed_view):
    # Send VC Proof messages to everyone
    # if my_info.last_installed == my_info.last_attempted:
    if not last_installed_queue.empty():
        last_installed = last_installed_queue.get()
    else:
        last_installed = last_installed_view
    # print("IN VC_PROOF SEND: Sending a vc_proof message with last_installed as:{0}".format(last_installed))
    vc_proof = VC_Proof(3, my_info.pid, last_installed)
    send_to_all_servers(vc_proof, all_hosts)
    threading.Timer(10.0, thread_send_vc_proof, args=(my_info, last_installed_queue, my_info.last_installed)).start()


# Read all hostnames from a file
def get_all_hosts(file_name):
    with open(file_name, 'r') as reader:
        list_of_hosts = reader.read().splitlines()
    return list_of_hosts


# Remove a container provided in the argument
def remove_node_from_list(list_of_nodes, node_to_remove):
    list_of_nodes.remove(node_to_remove)
    return list_of_nodes


# Function to clear the data structures for my process during view change
def clear_data_structures_for_vc(my_info):
    my_info.view_change_messages.clear()
    my_info.prepare_oks.clear()


# Function to apply the given view change message to the process's data structures
def apply_vc_to_data_structures(view_change_msg, my_info):
    # Remove any old vc messages if any
    for vc_msg in my_info.view_change_messages.values():
        if vc_msg.attempted < view_change_msg.attempted:
            if view_change_msg.server_id in my_info.view_change_messages:
                del my_info.view_change_messages[view_change_msg.server_id]
                print("Deleted old stuff")
    if view_change_msg.server_id in my_info.view_change_messages:
        return

    if my_info.test_case == 4 and (my_info.pid == 1 or my_info.pid == 2):
        if my_info.last_attempted == 1:
            if len(my_info.view_change_messages) == 2:
                print("Crashing after receiving 2 VC Messages....")
                exit(1)

    if my_info.test_case == 5 and (my_info.pid == 1 or my_info.pid == 2 or my_info.pid == 3):
        if my_info.last_attempted == 1:
            if len(my_info.view_change_messages) == 2:
                print("Crashing after receiving 2 VC Messages....")
                exit(1)

    my_info.view_change_messages[view_change_msg.server_id] = view_change_msg


# Function for initiating the leader election protocol
def shift_to_leader_election(view, all_hosts, my_info):
    my_info.state = LEADER_ELECTION
    clear_data_structures_for_vc(my_info)
    my_info.last_attempted = view
    vc = View_Change(2, my_info.pid, my_info.last_attempted)
    # print("Sending vc messages to everyone...")
    if my_info.test_case == 3 and my_info.pid == 1:
        if my_info.last_attempted == 1:
            exit(2)
    send_to_all_servers(vc, all_hosts)
    apply_vc_to_data_structures(vc, my_info)


# Function to handle any incoming View_Change messages
def handle_view_change_message(recvd_msg, my_info):
    # print("Received a View Change Message from {0}".format(address))
    # print("My Last Attempted : {0}, Received last attempted : {1} Sending_Server: {2}". format(my_info.last_attempted,
    #                                                                        recvd_msg.attempted, recvd_msg.server_id))
    vc_msg = View_Change(recvd_msg.type, recvd_msg.server_id, recvd_msg.attempted)
    if vc_msg.attempted == my_info.last_attempted:
        apply_vc_to_data_structures(vc_msg, my_info)


# Function to check if the process is ready for pre-installation of a view
def pre_install_ready(view, my_info):
    if len(my_info.view_change_messages) >= (int(total_hosts/2)+1):
        for vc in my_info.view_change_messages.values():
            if vc.attempted == view:
                continue
            else:
                return False
        return True


def leader_of_last_attempted(process_id, last_attempted, N, my_info):
    current_view_leader = last_attempted % N
    if process_id == current_view_leader:
        my_info.state = REG_LEADER
    return process_id == current_view_leader


# Print the current leader of this view
def print_leader(my_info):
    current_view_leader = my_info.last_attempted % total_hosts
    print("\n<{0}> :: Server {1} is the new leader of view {2}.\n".format(my_info.pid, current_view_leader,
                                                                      my_info.last_attempted))


# Function to handle VC_Proof Messages
def handle_vc_proof_messages(vc_proof_msg, my_info):
    if vc_proof_msg.installed > my_info.last_installed:
        my_info.last_attempted = vc_proof_msg.installed
        my_info.last_installed = vc_proof_msg.installed
        print("UPDATED VIEW TO: {0} ".format(my_info.last_attempted))
        if not my_info.set_timer:
            my_info.set_timer = True
        print_leader(my_info)


def leader_sent_vc_message(my_info):
    current_view_leader = my_info.last_attempted % total_hosts
    if current_view_leader in my_info.view_change_messages:
        return True
    return False


# Main function
if __name__ == '__main__':
    # Create a command line parser
    parser = argparse.ArgumentParser(description='Get current container name, hostfile and other stuff', add_help=False)
    # Add the arguments to be handled
    parser.add_argument('-h', type=str)
    parser.add_argument('-n', type=str)
    parser.add_argument('-t', type=int)
    args = parser.parse_args()

    # Set variables with the arguments
    host_file = args.h
    my_name = args.n
    test_case = args.t

    # Initialize all data structures for this process:
    process_id = int(my_name.split('r')[1])
    my_info = ProcessVariables(process_id)
    my_info.test_case = test_case
    print("My process_id is::{0}".format(my_info.pid))
    hosts = get_all_hosts(host_file)

    # Call a function to check if all the nodes are alive.
    print("Checking to see if all nodes are up...")
    # Remove my name from the list before checking
    hosts = remove_node_from_list(hosts, my_name)
    if are_all_nodes_up(hosts, my_info):
        print("All nodes are up")
    else:
        exit(1)

    # All nodes are up, get all the hosts and start the algorithm
    all_hosts = get_all_hosts(host_file)
    total_hosts = len(all_hosts)
    listening_socket = get_socket(True)
    inputs = [listening_socket]
    # Randomize time for initial loop:
    progress_timer = 10
    t = threading.Thread(target=timer_thread, args=(progress_timer,), name='T')
    t_new = threading.Thread()
    my_info.set_timer = True
    t.start()
    installed_queue = queue.Queue()

    vc_proof_thread = threading.Timer(10.0, thread_send_vc_proof, args=(my_info, installed_queue, my_info.last_installed))
    vc_proof_thread.start()
    vc_proof_flag = True
    while True:
        timeout = 5
        if (not t.is_alive()) and my_info.set_timer:
            my_info.set_timer = False
            print("\n Starting a new View Change...\n")

            # Handle all test cases here:
            if my_info.test_case == 1:
                if my_info.last_installed == 1 and my_info.last_attempted == 1:
                    print("Test Case 1 Completed!")
                    exit(1)

            if my_info.test_case == 2:
                if my_info.last_attempted == 5 and my_info.last_attempted == 5:
                    print("Test Case 2 Completed!")
                    exit(1)

            if my_info.test_case == 3 and my_info.pid == 1:
                if my_info.last_attempted == 0 and my_info.last_installed == 0:
                    print("Crashing before sending VC messages....\n")

            if my_info.test_case == 4 and (my_info.pid == 1 or my_info.pid == 2):
                if my_info.last_attempted == 0 and my_info.last_installed == 0:
                    print("Going to crash before receiving all VC Messages......\n")
            # print("Current last_installed : {0} last_attempted: {1}".format(my_info.last_installed,
            #                                                                 my_info.last_attempted))

            if my_info.test_case == 5 and (my_info.pid == 1 or my_info.pid == 2 or my_info.pid == 3):
                if my_info.last_attempted == 0 and my_info.last_installed == 0:
                    print("Going to crash before receiving all VC Messages......\n")

            shift_to_leader_election(my_info.last_attempted+1, all_hosts, my_info)

        # Select and start receiving different messages
        try:
            input_ready, _, _ = select.select(inputs, [], [], 5)
        except select.error as error:
            print("Error in select while running paxos :{0}".format(error))
        for s in input_ready:
            if s is listening_socket:
                msg, address = s.recvfrom(BUFFER_SIZE)
                recvd_msg = loads(msg)
                # If received message is a View_Change message
                if recvd_msg.type == 2:
                    handle_view_change_message(recvd_msg, my_info)
                    if pre_install_ready(recvd_msg.attempted, my_info):
                        # print(" \nPRE-INSTALL PHASE \n")
                        if not my_info.set_timer:
                            t = threading.Thread(target=timer_thread, args=(progress_timer,), name='T2')
                            t.start()
                            my_info.set_timer = True
                            # print("Checking to see if I am the leader for this view")
                            # print("Installing view {0}, since we have a majority of VC messages.".format(my_info.last_attempted))
                            my_info.last_installed = my_info.last_attempted
                            installed_queue.put(my_info.last_installed, block=False)
                            if leader_of_last_attempted(my_info.pid, my_info.last_attempted, total_hosts, my_info):
                                # print("I'M THE LEADER BITCH")
                                print_leader(my_info)
                            else:
                                my_info.state = REG_NON_LEADER
                                # Check if the leader exists in the VC messages, otherwise no one is the leader
                                # Implement this only if time permits, but otherwise, it is okay if you choose a leader
                                # that has crashed
                                # if leader_sent_vc_message(my_info):
                                print_leader(my_info)

                # If received message is a VC Proof message:
                if recvd_msg.type == 3:
                    # print("Received a VC Proof for Installed View: {0} message from {1}".format(recvd_msg.installed,
                    #                                                                             recvd_msg.server_id))
                    vc_proof_msg = VC_Proof(recvd_msg.type, recvd_msg.server_id, recvd_msg.installed)
                    handle_vc_proof_messages(vc_proof_msg, my_info)
                    # print("\n -------------------------------------------------")
                    # print("After handling VC Proof Message: Timer Flag: {0} Attempted: {1}  Installed: {2}\n"
                    #       .format(my_info.set_timer, my_info.last_attempted, my_info.last_installed))

