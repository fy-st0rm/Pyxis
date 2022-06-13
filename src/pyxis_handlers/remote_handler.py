# Pyxis api
from pyxis_api.pyxis_api   import *
from pyxis_api.conf		   import *
from pyxis_api.pyxis_const import *

class RemoteHandler:
	def __init__(self, database):
		self.database = database
		self.remotes = {}
		self.data_register = {}
	
	def get_remotes(self):
		return (self.remotes, len(self.remotes))

	def add_new_remote(self, conn, addr):
		self.remotes.update({conn: []})
		thread = threading.Thread(target = self.__handle_remote, args = (conn, addr))
		thread.start()
	
	def disconnect(self):
		for i in self.remotes:
			pyxis_send(i, pQuery([DISCONNECT], None))
	
	# Data register handlers
	def __rem_conn_from_register(self, conn):
		datas = self.remotes[conn]
		for data in datas:
			self.data_register[data[0]][data[1]].remove(conn)
		self.remotes.pop(conn)

	def __add_new_register(self, id, padd, total, file):
		self.data_register.update({id: {"padd": padd, "total": total, "file": file}})

	def __add_new_chunk(self, id, chunk_id):
		self.data_register[id].update({chunk_id: []})

	def __update_data_register(self, conn, datas):
		for data in datas:
			# Storing the data stored by connection for index purpose
			self.remotes[conn].append(data)

			# Adding the connection in the register for the data stored by the connection
			if data[0] not in self.data_register:
				self.__add_new_register(data[0], data[2], data[3], data[4])

			reg = self.data_register[data[0]]
			if data[1] not in reg:
				self.__add_new_chunk(data[0], data[1])
			
			chunk = reg[data[1]]
			if conn not in chunk:
				chunk.append(conn)

		# print(self.data_register)
		# print(self.remotes)
	
	# Remote handlers
	def __handle_remote(self, conn, addr):
		active = True
		while active:
			try:
				query = pyxis_recv(conn)

				# TODO: STORE and FETCH command will not be included for remote handler but will only be in remotes. THIS IS FOR TEST ONLY
				# Parsing the query
				if query.cmd[0] == STORE:
					res = self.database.query(query)
					pyxis_send(conn, res)

				elif query.cmd[0] == FETCH:
					res = self.database.query(query)
					pyxis_send(conn, res)

				elif query.cmd[0] == DATA:
					self.__update_data_register(conn, query.cmd[1])

				else:
					pyxis_send(conn, pResult(f"Unknown `{query.cmd[0], query.cmd[1]}`.", None, False))
			except EOFError:
				pyxis_error(f"Remote Handler: {addr} disconnected.")
				active = False

		# When remote gets disconnected
		self.__rem_conn_from_register(conn)
	
	# Distributes data to all remotes
	def distribute_data(self, file, data, pub_key):
		# TODO: Slow because of interation for all data 
		remotes = list(self.remotes.keys())

		# Sending data to all the remotes to store
		i = 0
		for j in data:
			query = pQuery([STORE, [file, j, data[j]]], pub_key)
			pyxis_send(remotes[i], query)
			i += 1
			if i >= len(remotes): i = 0

