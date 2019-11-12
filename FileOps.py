import pickle



def writeToFile(proces_valriable):


	try :
		with open("log","ab") as file:
			pickle.dump(proces_valriable,file)

	except Exception as e:
		print("error in writing to log file",e)



def readFromFile():
	objList = []
	try:
		with open("log","rb") as file:
			while(True):
				try:
					objList.append(pickle.load(file))
				except EOFError:
					break			
		return objList


	except Exception as e:
		print("error in reading from log file ", e)



