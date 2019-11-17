from NetworkFunctions import send_to_all_servers
from MessageFormats import Globally_Ordered_Update


# function to check for conflicts on getting an Accept
def check_conflicts_for_accept(my_info, accept_msg):
    if my_info.pid == accept_msg.server_id:
        return True
    if my_info.last_installed != accept_msg.view:
        return True
    if accept_msg.seq in my_info.global_history:
        if my_info.global_history[accept_msg.seq]['Proposal'] is not None:
            if my_info.global_history[accept_msg.seq]['Proposal'].view != accept_msg.view:
                print("Found a Proposal with the wrong view in global history of seq: {0}".format(accept_msg.seq))
                return True
    return False


# Function to apply Accept to data structures
def apply_accept_to_ds(my_info, accept_msg):
    seq = accept_msg.seq
    if accept_msg.seq in my_info.global_history:
        if my_info.global_history[seq]['Globally_Ordered_Update'] is not None:
            return
        if len(my_info.global_history[seq]['Accepts']) >= int(len(my_info.all_hosts)/2):
            return
        # Check if the accept received is already present in accepts[]
        for accept in my_info.global_history[seq]['Accepts']:
            if accept.server_id == accept_msg.server_id:
                return
        my_info.global_history[seq]['Accepts'].append(accept_msg)
    else:
        my_info.global_history[seq] = my_info.global_history_dict
        my_info.global_history[seq]['Accepts'].append(accept_msg)


# Function to check if the update is ready to be globally ordered
def globally_ordered_update(my_info, accept_msg):
    seq = accept_msg.seq
    if seq in my_info.global_history:
        if my_info.global_history[seq]['Proposal'] is not None:
            if len(my_info.global_history[seq]['Accepts']) >= int(len(my_info.all_hosts)/2):
                # Check is each accept in seq has the same view
                for accept in my_info.global_history[seq]['Accepts']:
                    if accept.view == accept_msg.view:
                        continue
                    else:
                        return False
                return True
    else:
        return False


# Function to apply the globally ordered update to data structures
def apply_globally_ordered_update_to_ds(my_info, gbu):
    if gbu.seq in my_info.global_history:
        if my_info.global_history[gbu.seq]['Globally_Ordered_Update'] is None:
            my_info.global_history[gbu.seq]['Globally_Ordered_Update'] = gbu
            # Add another queue here


# Advance ARU
def advance_aru(my_info):
    i = my_info.local_aru + 1
    while True:
        if i in my_info.global_history and my_info.global_history[i]['Globally_Ordered_Update'] is not None:
            my_info.local_aru = my_info.local_aru + 1
            i = i + 1
        else:
            return


# Function to handle accept message when received:
def handle_accept(my_info, accept_msg):
    print("Handling Accept")
    apply_accept_to_ds(my_info, accept_msg)
    if globally_ordered_update(my_info, accept_msg):
        # At this point, the client update should be present in the Proposal message that has been stored in
        # Global history for a particular seq number under 'Proposal'
        client_update = my_info.global_history[accept_msg.seq]['Proposal']
        globally_ordered_client_update = Globally_Ordered_Update(10, my_info.pid, accept_msg.seq,  client_update)
        apply_globally_ordered_update_to_ds(my_info, globally_ordered_client_update)
        advance_aru(my_info)
        print("Update globally ordered, current ARU: {0}   GBU_Seq:{1}".format(my_info.local_aru,
                                                                      globally_ordered_client_update.seq))
    else:
        print("Update not globally ordered yet")
