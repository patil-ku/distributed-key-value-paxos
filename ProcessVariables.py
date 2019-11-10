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
        self.prepare_oks = {}
        self.set_timer = False
        self.local_aru = 0
