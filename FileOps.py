import pickle


def writeToFile(data):
	try :
		with open("log","ab") as file:
			pickle.dump(data,file)

	except Exception as e:
		print("error in writing to log file",e)


# def readFromFile():
# 	objList = []
# 	try:
# 		with open("log","rb") as file:
# 			while(True):
# 				try:
# 					objList.append(pickle.load(file))
# 				except EOFError:
# 					break			
# 		return objList
# 	except Exception as e:
# 		print("error in reading from log file ", e)

def readFromFile():
	server_info = None
	try:
		with open("log","rb") as file:
			server_info = pickle.load(file)

	except Exception as e:
		print("error in reading from log file ", e)

	return server_info


# Dummy operation to write incoming data to a file
def write_to_file_dummy(data):
	try:
		f = open("test.txt", "a")
		f.write(str(data))
		print("Write Successful")
	except Exception as e:
		print("Error in writing dummy data to file: {0}".format(e))
