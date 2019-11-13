from MessageFormats import ClientUpdate



def enqueueUpdate(client_update,server_info):

	if(client_update.timestamp <= server_info.last_executed[client_update.client_id]):
		return False

	if(client_update.timestamp <= server_info.last_enqueued[client_update.client_id]):
		return False


	#adding client to upddate queue
	server_info.update_queue.append(client_update)
	server_info.last_enqueued[client_update.client_id] = client_update.timestamp
	return True

def addToPendingUpdates(client_update,server_info):
	server_info.pending_updates[client_update.client_id] = client_update

	##Set Update Timer(U.client id)
	##Sync to disk







def handleClientUpdates(client_update,server_info):

	if(server_info.state == LEADER_ELECTION):
		if(client_update.server_id != server_info.pid):
			print("received client update {0} to wrong server {1}".format(client_update.server_id,server_info.pid))
			return 

		if(enqueueUpdate(client_update)):
			addToPendingUpdates(client_update)


	if(server_info.state = REG_NON_LEADER):
		if(client_update.server_id == server_info.pid):
			## SEND to Leader

	if(server_info.state = REG_LEADER):

		if(enqueueUpdate(client_update)):
			if(client_update.server_id ==  server_info.pid):
				addToPendingUpdates(client_update)

			#sendProposal()






	
