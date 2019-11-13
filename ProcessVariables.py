import MessageFormats

REG_LEADER = 1
REG_NON_LEADER = 2
LEADER_ELECTION = 3


class ProcessVariables:

    def __init__(self, process_id):
        self.pid = process_id
        self.state = LEADER_ELECTION
        self.last_installed = -1
        self.last_attempted = -1
        self.view_change_messages = {}
        # Initial Prepare message here
        self.prepare = MessageFormats.Prepare_Message(7, process_id, -1, -1)
        #Global Ordering variables
        self.prepare_oks = {}
        self.set_timer = False
        self.local_aru = 0
        self.global_history = {}    #dict of global slots, mapped by sequence number, each containing
                                    #Proposal - latest Proposal accepted for this sequence number, if any
                                    #Accepts[] - array of corresponding Accept messages, indexed by server id
                                    #Globally Ordered Update - ordered update for this sequence number, if any
        #Client Handling variables
        self.update_queue = []      #queue of Client Update messages
        self.last_executed = {}     #dict of timestamps, mapped by client id, i.e client_id : timestamp
        self.last_enqueued = {}     #dict of timestamps, mapped by client id, i.e client_id : timestamp
        self.pending_updates = {}   #dict of Client Update messages, indexed by client id, i.e cloent_id : update