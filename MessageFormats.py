class Message:

    # Type 4 = Alive Message
    # Type 5 = AliveAck Message
    def __init__(self, type):
        self.type = type


class AliveMessage(Message):
    pass


class AliveAckMessage(Message):
    pass


# Type = 2
class View_Change(Message):

    def __init__(self, type, server_id, attempted ):
        super(View_Change, self).__init__(type)
        self.server_id = server_id
        self.attempted = attempted


# Type = 3
class VC_Proof(Message):

    def __init__(self, type, server_id, installed):
        super(VC_Proof, self).__init__(type)
        self.server_id = server_id
        self.installed = installed


# Type = 6
class LeaderInstall(Message):

    def __init__(self, type, server_id, view_to_install):
        super(LeaderInstall, self).__init__(type)
        self.server_id = server_id
        self.view_to_install = view_to_install


# Type = 7
class Prepare_Message(Message):

    def __init__(self, type, server_id, view, local_aru):
        super(Prepare_Message, self).__init__(type)
        self.server_id = server_id
        self.view = view
        self.local_aru = local_aru


# Type = 8: Prepare_OK
class Prepare_OK(Message):
    def __init__(self, type, server_id, view, data_list):
        super(Prepare_OK, self).__init__(type)
        self.server_id = server_id
        self.view = view
        self.data_list = data_list
