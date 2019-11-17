from MessageFormats import Client_Update, Proposal
from FileOps import write_to_file_dummy
from pickle import loads
from ProcessVariables import LEADER_ELECTION, REG_LEADER, REG_NON_LEADER
from NetworkFunctions import send_message_using_hostname
from Proposal import send_proposals


# Function to enqueue the update
def enqueue_update(client_update, server_info):
    if client_update.client_id in server_info.last_executed:
        if client_update.timestamp <= server_info.last_executed[client_update.client_id]:
            return False

    if client_update.client_id in server_info.last_enqueued:
        if client_update.timestamp <= server_info.last_enqueued[client_update.client_id]:
            return False
    server_info.update_queue.append(client_update)
    server_info.last_enqueued[client_update.client_id] = client_update.timestamp
    return True


# Function to add the pending updates to the server
def add_to_pending_updates(client_update, server_info):
    server_info.pending_updates[client_update.client_id] = client_update
    # Set Update Timer(U.client id)
    # Sync to disk


# Function to handle client update according to the state the server is in
def handle_client_updates(client_update, my_info):
    if my_info.state == LEADER_ELECTION:
        if client_update.server_id == my_info.pid:
            if enqueue_update(client_update, my_info):
                add_to_pending_updates(client_update, my_info)

    if my_info.state == REG_NON_LEADER:
        if client_update.server_id == my_info.pid:
            add_to_pending_updates(client_update, my_info)
            send_message_using_hostname(client_update, my_info.current_leader_hostname)

    if my_info.state == REG_LEADER:
        print("Got a client update from a non leader")
        if enqueue_update(client_update, my_info):
            if client_update.server_id == my_info.pid:
                add_to_pending_updates(client_update, my_info)
            print("Received a Client Update when I'm the leader, need to send proposals now...")
            # Make a proposal: server_id,view,seq,update
            send_proposals(my_info)


# Dummy method for testing
def handle_client_write_updates(write_msg, my_info):
    print("Inside client write update")
    my_info.seq_no += 1
    write_to_file_dummy(write_msg.data)
