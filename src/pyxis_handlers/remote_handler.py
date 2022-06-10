# Pyxis api
from pyxis_api.pyxis_api import *
from pyxis_api.conf		 import *

class RemoteHandler:
	def __init__(self, database):
		self.database = database
		self.remotes = {}
	
	def get_remotes(self):
		return (self.remotes, len(self.remotes))
	
	def __handle_remote(self, conn, addr):
		active = True
		while active:
			time.sleep(DELAY)
			query = pickle.loads(conn.recv(BUFF_CAP))

			# Parsing the query
			if query.cmd[0] == "STORE":
				self.database.query(query)

		self.remotes.pop(addr)
	
	def distribute_data(self, data, pub_key):
		# TODO: Slow because of interation for all data 
		remotes = list(self.remotes.values())

		# Sending data to all the remotes to store
		i = 0
		for j in data:
			query = pQuery(["STORE", j], pub_key)
			remotes[i].send(pickle.dumps(query))
			i += 1
			if i >= len(remotes): i = 0

	def add_new_remote(self, conn, addr):
		self.remotes.update({addr: conn})
		thread = threading.Thread(target = self.__handle_remote, args = (conn, addr))
		thread.start()
