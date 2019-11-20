from FileOps import readFromFile
from ProcessVariables import ProcessVariables
from ViewChange import shift_to_leader_election
import os.path


def recover(all_hosts,pid):
	my_info = None
	if(os.path.isfile("log")):
		my_info = readFromFile()
		if(not my_info):
			print("no data found in log, initialising data .. ")
			my_info = ProcessVariables(pid)
		else:
			#considering we get a single element for now
			shift_to_leader_election(my_info.last_installed+1,all_hosts,my_info)		
	else:
		print("log does not exist, initialising data .. ")
		my_info = ProcessVariables(pid)

	return my_info


