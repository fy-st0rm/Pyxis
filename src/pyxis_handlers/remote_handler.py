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

	def add_new_remote(self, conn):
		self.remotes.update({conn: []})

	def disconnect(self):
		pyxis_warning("IMPLEMENT DISCONNECT FUNCTION IN REMOTE HANDLER")

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
	
	# Query parser
	def parse_query(self, conn, qry):
		if qry.cmd == REG_DATA:
			self.__update_data_register(conn, qry.params)
			return pQuery(qry.to, qry.by, SUCESS, ["Sucessfully added the data into remote register."], None)
		else:
			return pQuery(qry.to, qry.by, FAILED, [f"Unknown `remote handler` command: {qry.cmd}"], None)

