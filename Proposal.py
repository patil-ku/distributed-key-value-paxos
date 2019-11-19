from NetworkFunctions import send_to_all_servers, send_message
from MessageFormats import Proposal, Accept
from ProcessVariables import REG_NON_LEADER
from FileOps import writeToFile


# Message to send the proposals:
def send_proposals(my_info):
    # Maybe we don't need the seq in myINfo?
    # my_info.seq = my_info.last_proposed + 1
    seq = my_info.last_proposed + 1

    if seq in my_info.global_history:
        if my_info.global_history[seq]['Globally_Ordered_Update'] is not None:
            my_info.last_proposed = my_info.last_proposed + 1
            send_proposals(my_info)

    if seq in my_info.global_history:
        if my_info.global_history[seq]['Proposal'] is not None:
            u = my_info.global_history[seq]['Proposal'].update
        elif not my_info.update_queue:
            return
        else:
            u = my_info.update_queue.pop()
    elif not my_info.update_queue:
        return
    else:
        u = my_info.update_queue.pop()

    proposal = Proposal(9, my_info.pid, my_info.last_installed, seq, u)
    apply_proposal_to_ds(my_info, proposal)
    my_info.last_proposed = seq
    my_info.seq = seq
    # **SYNC to disk
    writeToFile(my_info)
    print("Sending proposal to everyone now...")
    send_to_all_servers(proposal, my_info.all_hosts)


# Apply Proposal to data structures
def apply_proposal_to_ds(my_info, proposal):
    if proposal.seq in my_info.global_history:
        if my_info.global_history[proposal.seq]['Globally_Ordered_Update'] is not None:
            return
        if my_info.global_history[proposal.seq]['Proposal'] is not None:
            p1 = my_info.global_history[proposal.seq]['Proposal']
            if proposal.view > p1.view:
                my_info.global_history[proposal.seq]['Proposal'] = proposal
                my_info.global_history[proposal.seq]['Accepts'].clear()
        else:
            my_info.global_history[proposal.seq]['Proposal'] = proposal
        print("Done applying some updates by a Proposal")
    else:
        print("No data structures were updated on getting a proposal, adding the global history with"
              " seq number {0} now...".format(proposal.seq))
        my_info.global_history[proposal.seq] = my_info.global_history_dict
        my_info.global_history[proposal.seq]['Proposal'] = proposal


# Function to check for conflicts when a proposal is received:
def check_conflict_for_proposal(my_info, proposal):
    if my_info.pid == proposal.server_id:
        return True
    if my_info.state != REG_NON_LEADER:
        return True
    if my_info.last_installed != proposal.view:
        return True
    return False


# Function to handle the received proposal messages:
def handle_proposal(my_info, proposal):
    apply_proposal_to_ds(my_info, proposal)
    accept_msg = Accept(11, my_info.pid, proposal.view, proposal.seq)
    # *** SYNC TO DISK
    send_to_all_servers(accept_msg, my_info.all_hosts)


