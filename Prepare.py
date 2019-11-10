from ProcessVariables import LEADER_ELECTION, REG_LEADER
from MessageFormats import Prepare_Message, Prepare_OK
from NetworkFunctions import send_message, send_to_all_servers

# Flag only used for checking if the leader has installed the view, this is to prevent the leader to go into
# shift_to_reg_leader() every time a prepare ok comes after majority is reached.

leader_view_installed = False

# Print the current leader of this view
def print_leader(my_info, total_hosts):
    current_view_leader = my_info.last_attempted % total_hosts
    print("\n<{0}> :: Server {1} is the new leader of view {2}.\n".format(my_info.pid, current_view_leader,
                                                                      my_info.last_attempted))


# Check for conflicts in the received prepare message
def check_conflict_for_prepare_message(prepare_msg, my_info):
    if prepare_msg.server_id == my_info.pid:
        return True
    if prepare_msg.view != my_info.last_attempted:
        return True
    return False


# Update data structures for a prepare message:
def update_prepare_to_data_structures(prepare_msg, my_info):
    my_info.prepare = prepare_msg


# Update data structures on receiving a prepare ok:
def update_prepare_ok_to_data_structures(prepare_ok_msg, my_info):
    if prepare_ok_msg.server_id not in my_info.prepare_oks:
        my_info.prepare_oks[prepare_ok_msg.server_id] = prepare_ok_msg
        # Update data list here - Have to add


# Handle prepare_ok messages here:
def handle_prepare_ok(prepare_ok_msg, my_info, all_hosts):
    update_prepare_ok_to_data_structures(prepare_ok_msg, my_info)
    global leader_view_installed
    if not leader_view_installed:
        if view_prepared_ready(prepare_ok_msg.view, my_info, len(all_hosts)):
            print("\nPrepare phase over, let's shift to leader....\n")
            print_leader(my_info, len(all_hosts))


# Check if you have received enough prepare_oks
def view_prepared_ready(view, my_info, total_hosts_number):
    if len(my_info.prepare_oks) >= (int(total_hosts_number / 2) + 1):
        for po in my_info.prepare_oks.values():
            if po.view == view:
                continue
            else:
                return False
        global leader_view_installed
        leader_view_installed = True
        return True


def handle_prepare_message(prepare_msg, my_info, address, total_hosts):
    print("Handling prepare message")
    if my_info.state == LEADER_ELECTION:
        update_prepare_to_data_structures(prepare_msg, my_info)
        # Will add data_list stuff later
        prepare_ok = Prepare_OK(8, my_info.pid, prepare_msg.view, [])
        my_info.prepare_oks[my_info.pid] = prepare_ok
        # Shift to reg_leader (Will add a function later)
        my_info.state = REG_LEADER
        print("Sending Prepare OK to leader...")
        send_message(prepare_ok, address)
        print_leader(my_info, total_hosts)
    else:
        # Already installed the view
        prepare_ok = my_info.prepare_oks.get(my_info.pid)
        send_message(prepare_ok, address)
        print_leader(my_info, total_hosts)


# Shift to prepare phase for leader:
def shift_to_prepare_phase(my_info, all_hosts):
    print("In prepare phase, getting ready to send prepare to all servers...")
    my_info.last_installed = my_info.last_attempted
    prepare_msg = Prepare_Message(7, my_info.pid, my_info.last_installed, my_info.local_aru)
    update_prepare_to_data_structures(prepare_msg, my_info)
    # Update data list here, for now sending []
    prepare_ok = Prepare_OK(8, my_info.pid, my_info.last_installed, [])
    my_info.prepare_oks[my_info.pid] = prepare_ok
    # Clear last_enqueued
    # Sync to disk
    send_to_all_servers(prepare_msg, all_hosts)
