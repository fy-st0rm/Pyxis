# Pyxis api
from pyxis_api.pyxis_api   import *
from pyxis_api.conf		   import *
from pyxis_api.pyxis_const import *

class RemoteHandler:
	def __init__(self, database):
		self.database = database
		self.remotes = {}
		self.data_register = {}
		self.fetched_data = {}
	
	def get_remotes(self):
		return (self.remotes, len(self.remotes))

	def add_new_remote(self, conn):
		self.remotes.update({conn: []})
	
	def remove_conn(self, conn):
		datas = self.remotes[conn]
		for data in datas:
			self.data_register[data[0]][data[1]].remove(conn)
		self.remotes.pop(conn)

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
	
	# Data distributor
	def distribute_data(self, chunks, pub_key):
		remotes = list(self.remotes.keys())

		# Sending data to all the remotes to store
		i = 0
		for j in chunks:
			qry = pQuery(REM_HANDLER, REMOTE, STORE, [j, chunks[j]], pub_key)
			pyxis_send(remotes[i], qry)

			i += 1
			if i >= len(remotes): i = 0

		return pQuery(REM_HANDLER, PYX_DATABASE, SUCESS, ["Sucessfully stored in all remotes."], None)
	
	# Data receiver
	def __gather_fetched(self, qry):
		# Gatthers the fetched data incoming from remotes and saves in an interneal memory
		uid = qry.params[0]
		chunk = qry.params[1]
		pub_key = qry.params[2]
		data = qry.params[3]
		self.fetched_data[uid].update({chunk: data})
		self.fetched_data[uid].update({"key": pub_key})

	def __handle_fetched_failed(self, qry):
		uid = qry.params[0]
		self.fetched_data[uid]["progress"] = False
		self.fetched_data[uid]["msg"] = qry.params[1]

	def fetch_data(self, uid, pub_key):
		# Assigns the remotes to fetch for the required data
		reg = self.data_register[uid]
		total = int(reg["total"])

		if uid not in self.fetched_data:
			self.fetched_data.update({uid: {"progress": True, "msg": None, "key": None}})

			for i in range(total):
				conn = random.choice(reg[str(i)])
				pyxis_send(conn, pQuery(REM_HANDLER, REMOTE, FETCH, [uid, str(i)], pub_key))
	
	def retrive_fetched_data(self, uid, pub_key):
		# Asking for the data only if data is completely gathered
		total = int(self.data_register[uid]["total"]) 

		# Waiting for the data to be complete
		while len(self.fetched_data[uid]) - 3 != total: 
			if not self.fetched_data[uid]["progress"]:
				return pQuery(PYX_DATABASE, REM_HANDLER, FAILED, [self.fetched_data[uid]["msg"]], None)

		# Password checking
		if pub_key != self.fetched_data[uid]["key"]:
			return pQuery(PYX_DATABASE, REM_HANDLER, FAILED, [f"Wrong public key was used to fetch data of uid: {uid}"], None)

		# Making chunks
		chunks = []
		for i in self.fetched_data[uid]:
			if i not in ["progress", "msg", "key"]:
				chunks.append(self.fetched_data[uid][i])

		return pQuery(PYX_DATABASE, REM_HANDLER, SUCESS, chunks, None)
	
	# Query parser
	def parse_query(self, conn, qry):
		if qry.cmd == REG_DATA:
			self.__update_data_register(conn, qry.params)
			return pQuery(qry.to, qry.by, SUCESS, ["Sucessfully added the data into remote register."], None)
		elif qry.cmd == FETCHED:
			self.__gather_fetched(qry)
			return pQuery(qry.to, qry.by, SUCESS, ["Sucessfully added the data into fetched database."], None)
		elif qry.cmd == FETCHED_FAILED:
			self.__handle_fetched_failed(qry)
			return pQuery(qry.to, qry.by, SUCESS, ["Sucessfully assigned the fetched failed command."], None)
		else:
			return pQuery(qry.to, qry.by, FAILED, [f"Unknown `remote handler` command: {qry.cmd}"], None)
