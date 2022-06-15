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
		self.results = {}
	
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
	
	# Result handler
	def __handle_result(self, qry):
		pub_key = qry.auth
		cmd = qry.params[0]
		msg = qry.params[1]

		reg = self.results[pub_key][cmd]

		if qry.cmd == SUCESS:
			reg["msg"] = msg
			reg["res"].append(True)
		elif qry.cmd == FAILED:
			reg["msg"] = msg
			reg["progress"] = False
	
	def get_result(self, cmd, pub_key):
		if pub_key not in self.results:
			return pQuery(REM_HANDLER, PYX_DATABASE, FAILED, [f"{pub_key} is an invalid process executioner."], None)
		
		if cmd not in self.results[pub_key]:
			return pQuery(REM_HANDLER, PYX_DATABASE, FAILED, [f"{cmd} is an invalid process by owner of key {pub_key}."], None)

		reg = self.results[pub_key][cmd]
		while len(reg["res"]) != len(self.remotes):
			if not reg["progress"]: 
				msg = reg["msg"]
				return pQuery(REM_HANDLER, PYX_DATABASE, FAILED, [f"Failed to execute cmd `{cmd}` due to `{msg}`."], None)

		# Removing the process
		self.results[pub_key].pop(cmd)

		return pQuery(REM_HANDLER, PYX_DATABASE, SUCESS, [f"Sucessfully executed cmd `{cmd}`."], None)

	# Data distributor
	def distribute_data(self, chunks, pub_key):
		remotes = list(self.remotes.keys())
		
		# Getting ready to handle the results
		if pub_key not in self.results:
			self.results.update({pub_key: {}})
		self.results[pub_key].update({STORE: {"progress": True, "msg": None, "res": []}})

		# Sending data to all the remotes to store
		i = 0
		for j in chunks:
			qry = pQuery(REM_HANDLER, REMOTE, STORE, [j, chunks[j]], pub_key)
			pyxis_send(remotes[i], qry)

			i += 1
			if i >= len(remotes): i = 0
	
	# Data receiver
	def __gather_fetched(self, qry):
		# Gatthers the fetched data incoming from remotes and saves in an interneal memory
		uid     = qry.params[0]
		chunk   = qry.params[1]
		pub_key = qry.params[2]
		data    = qry.params[3]
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

	# Data destroyer
	def delete_data(self, uid, pub_key):
		# Getting ready to handle the results
		if pub_key not in self.results:
			self.results.update({pub_key: {}})
		self.results[pub_key].update({DELETE: {"progress": True, "msg": None, "res": []}})
		
		# Removing file form memory
		if uid in self.fetched_data:
			if pub_key == self.fetched_data[uid]["key"]:
				self.fetched_data.pop(uid)

		# Instructing all the remotes having the file to delete it
		reg = self.data_register[uid]
		for i in reg:
			if i not in ["padd", "total", "file"]:
				conns = reg[i]
				for conn in conns:
					pyxis_send(conn, pQuery(REM_HANDLER, REMOTE, DELETE, [uid], pub_key))
	
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

		elif qry.cmd == SUCESS or qry.cmd == FAILED:
			self.__handle_result(qry)
			return pQuery(qry.to, qry.by, SUCESS, [f"Sucessfully assigned `{qry.cmd}` the command."], None)

		else:
			return pQuery(qry.to, qry.by, FAILED, [f"Unknown `remote handler` command: {qry.cmd}"], None)
