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
        # Prepare message here, not sure how this will be implemented.
        self.prepare_oks = {}
        self.set_timer = False
        self.test_case = 0
