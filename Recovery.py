from FileOps import readFromFile
from ProcessVariables import ProcessVariables
from ViewChange import shift_to_leader_election
import os.path


def recover(all_hosts,pid):
	my_info = None
	if(os.path.isfile("log")):
		proc_valriable_list = readFromFile()
		if(not proc_valriable_list):
			print("no data found in log, initialising data .. ")
			my_info = ProcessVariables(pid)
		else:
			#considering we get a single element for now
			my_info = proc_valriable_list[0]
			shift_to_leader_election(my_info.last_installed+1,all_hosts,my_info)		
	else:
		print("log does not exist, initialising data .. ")
		my_info = ProcessVariables(pid)

	return my_info


