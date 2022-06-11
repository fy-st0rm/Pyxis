# Pyxis api
from pyxis_api.pyxis_api   import *
from pyxis_api.conf		   import *
from pyxis_api.pyxis_const import *

class RemoteHandler:
	def __init__(self, database):
		self.database = database
		self.remotes = {}
	
	def get_remotes(self):
		return (self.remotes, len(self.remotes))
	
	def __handle_remote(self, conn, addr):
		active = True
		while active:
			try:
				query = pyxis_recv(conn)

				# Parsing the query
				if query.cmd[0] == STORE:
					pyxis_send(conn, pResult(f"Storing data...", None, True))
					res = self.database.query(query)
					pyxis_send(conn, res)
				else:
					pyxis_send(conn, pResult(f"Unknown `{cmd[0]}`.", None, False))
			except EOFError:
				pyxis_error(f"Remote Handler: {addr} disconnected.")
				active = False

		self.remotes.pop(addr)
	
	def distribute_data(self, data, pub_key):
		# TODO: Slow because of interation for all data 
		remotes = list(self.remotes.values())

		# Sending data to all the remotes to store
		i = 0
		for j in data:
			query = pQuery([STORE, [j, data[j]]], pub_key)
			pyxis_send(remotes[i], query)
			i += 1
			if i >= len(remotes): i = 0

	def add_new_remote(self, conn, addr):
		self.remotes.update({addr: conn})
		thread = threading.Thread(target = self.__handle_remote, args = (conn, addr))
		thread.start()
	
	def disconnect(self):
		remotes = list(self.remotes.values())
		for i in remotes:
			pyxis_send(i, pQuery([DISCONNECT], None))

