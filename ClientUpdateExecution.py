
# Maintain this file to execute client updates
from ProcessVariables import LEADER_ELECTION, REG_LEADER
from Proposal import send_proposals
from NetworkFunctions import send_message


PORT = 9999


def execute_client_update(my_info, accept_msg):
    print("Getting the update")
    seq = accept_msg.seq
    client_update = my_info.global_history[seq]['Proposal'].update
    print("--------------------------------")
    print("Client details: client_id:{0}  server_id:{1}  timestamp:{2}   update{3}".format(client_update.client_id,
                                                                                           client_update.server_id,
                                                                                           client_update.timestamp,
                                                                                           client_update.update))
    print("-------------------------------- \n")
    upon_executing_client_update(my_info,  client_update)


# Function to reply to client
def reply_to_client(my_info, client_update):
    client_address = my_info.client_map[client_update.client_id]
    # Dummy, add a message format later
    msg = "SUCCESS for timestamp: {0} update:{1}".format(client_update.timestamp, client_update.update)
    send_message(msg, client_address)


# Function to execute after the client update is executed
def upon_executing_client_update(my_info, client_update):
    advance_aru(my_info)
    if client_update.server_id == my_info.pid:
        # Reply to client with a success message: use the map stored in my_info
        reply_to_client(my_info, client_update)
        print("Success message sent to client for client_id:{0} and timestamp:{1} and address: {2}"
              .format(client_update.client_id, client_update.timestamp, my_info.client_map[client_update.client_id]))
        if client_update in my_info.pending_updates.values():
            # Cancel Update Timer
            # Remove this update from the pending updates list
            temp_dict = my_info.pending_updates
            my_info.pending_updates = {key: val for key, val in temp_dict.items() if val != client_update}

    my_info.last_executed[client_update.client_id] = client_update.timestamp
    if my_info.state != LEADER_ELECTION:
        print("Need to restart progress_timer")
        # Figure out how to restart progress timer
    if my_info.state == REG_LEADER:
        send_proposals(my_info)
    print("Done executing Client Update")


# Advance ARU
def advance_aru(my_info):
    i = my_info.local_aru + 1
    while True:
        if i in my_info.global_history and my_info.global_history[i]['Globally_Ordered_Update'] is not None:
            my_info.local_aru = my_info.local_aru + 1
            i = i + 1
        else:
            return
