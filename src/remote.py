# pyxis api
from pyxis_api.pyxis_types import *
from pyxis_api.pyxis_const import *
from pyxis_api.pyxis_api   import *

class Remote:
	def __init__(self):
		self.api = Pyxis_API()
		self.active = True
		self.queries = []
		self.results = []
	
	# Connect and Disconnect functions with pyxis server
	def __connect(self):
		qry = pQuery(REMOTE, PYX_SERVER, CONNECT, [REMOTE], None)
		res = self.api.query(qry)
		if res.cmd == SUCESS:
			pyxis_sucess(res.params[0])
		else:
			pyxis_error(res.params[0])
			exit(1)

	def __disconnect(self):
		qry = pQuery(REMOTE, PYX_SERVER, DISCONNECT, None, None)
		res = self.api.query(qry)
		if res.cmd == SUCESS:
			pyxis_sucess(res.params[0])
		else:
			pyxis_error(res.params[0])
			exit(1)

	# Registration function
	def __load_stored_data(self):
		data = []
		path = pyxis_get_storage_path(platform.system())
		files = os.listdir(path)

		for i in files:
			f_info = i.split(":")
			id     = f_info[0]
			chunk  = f_info[1]
			padd   = f_info[2]
			total  = f_info[3]
			file   = f_info[4]
			data.append((id, chunk, padd, total, file))

		return data
	
	def __register_data(self):
		data = self.__load_stored_data()
		qry  = pQuery(REMOTE, REM_HANDLER, REG_DATA, data, None) 
		pyxis_send(self.api.server, qry)
	
	# Storing and fetching
	def __load_zip(self, path, file, pub_key):
		with pyzipper.AESZipFile(path + file) as zf:
			zf.setpassword(pub_key.encode())
			data = zf.read(file.strip(".zip"))
		return data

	def __store(self, qry):
		try:
			pub_key = qry.auth
			name = qry.params[0]
			data = qry.params[1]
			path = pyxis_get_storage_path(platform.system())

			pyxis_sucess("Compressing and encrypting.")
			with pyzipper.AESZipFile(path + name + ".zip", "w", compression=pyzipper.ZIP_LZMA, encryption=pyzipper.WZ_AES) as zf:
				zf.setpassword(pub_key.encode())
				zf.writestr(name, data)
			pyxis_sucess("Sucessfully stored data.")

			return pQuery(REMOTE, REM_HANDLER, SUCESS, [STORE, f"Sucessfully stored in remote."], qry.auth)
		except Exception as e:
			return pQuery(REMOTE, REM_HANDLER, FAILED, [STORE, f"Failed to store in remote.\nReason: {e}"], qry.auth)

	def __fetch(self, qry):
		uid = qry.params[0]
		idx = qry.params[1]
		pub_key = qry.auth

		path = pyxis_get_storage_path(platform.system())
		files = os.listdir(path)

		# Looping through every file and matching the chunk and the uid 
		for i in files:
			f_info = i.split(":")
			id     = f_info[0]
			chunk  = f_info[1]

			if uid == id and idx == chunk:
				try:
					data = self.__load_zip(path, i, pub_key)
					res = pQuery(REMOTE, REM_HANDLER, FETCHED, [uid, idx, pub_key, data], None)
					return res

				except Exception as e:
					res = pQuery(REMOTE, REM_HANDLER, FETCHED_FAILED, [uid, f"Error fetching from remote.\nReason: {e}"], None)
					return res

		return pQuery(REMOTE, REM_HANDLER, FETCHED_FAILED, [uid, f"File with uid: {uid} and chunk: {idx} is not located in this remote."], None)

	def __delete(self, qry):
		uid = qry.params[0]
		pub_key = qry.auth

		path = pyxis_get_storage_path(platform.system())
		files = os.listdir(path)

		for i in files:
			if uid in i:
				try:
					# Trying to read the file to check if the key is correct or not
					data = self.__load_zip(path, i, pub_key)
					os.remove(path + i)
					return pQuery(REMOTE, REM_HANDLER, SUCESS, [DELETE, f"Sucessfully deleted file with uid {uid}."], pub_key)
				except Exception as e:
					return pQuery(REMOTE, REM_HANDLER, FAILED, [DELETE, f"Failed to delete file with uid {uid}\nReason: {e}"], pub_key)
	
	# Listener for remote handler
	def __check_for_register(self):
		while REG_SUCESS not in self.results: pass 
		self.results.pop()

	def __handle_store(self, qry):
		res = self.__store(qry)
		pyxis_sucess("STORE: Registrating data")
		self.__register_data()
		self.__check_for_register()
		pyxis_sucess("STORE: Sending result")
		pyxis_send(self.api.server, res)
	
	def __handle_fetch(self, qry):
		res = self.__fetch(qry)
		pyxis_sucess("FETCH: Sending result")
		pyxis_send(self.api.server, res)

	def __handle_delete(self, qry):
		res = self.__delete(qry)
		pyxis_sucess("DELETE: Registrating data")
		self.__register_data()
		self.__check_for_register()
		pyxis_sucess("DELETE: Sending result")
		pyxis_send(self.api.server, res)
	
	def __handle_process(self):
		while self.active:
			if len(self.queries) > 0:
				recv = self.queries.pop()
				if recv.cmd == STORE:
					self.__handle_store(recv)

				elif recv.cmd == FETCH:
					self.__handle_fetch(recv)

				elif recv.cmd == DELETE:
					self.__handle_delete(recv)

	def __listen(self):
		thread = threading.Thread(target = self.__handle_process)
		thread.start()

		while self.active:
			recv = pyxis_recv(self.api.server)
			pyxis_send(self.api.server, pQuery(REMOTE, REM_HANDLER, REPLY, [f"Query has been reached."], None))
			if recv.cmd == REG_SUCESS:
				self.results.append(REG_SUCESS)
			else:
				self.queries.append(recv)
	
	def run(self):
		try:
			self.__connect()

			data = self.__load_stored_data()
			qry  = pQuery(REMOTE, REM_HANDLER, REG_DATA, data, None) 
			recv = self.api.query(qry)
			if recv.cmd == REG_SUCESS:
				pyxis_sucess(recv.params[0])
			else:
				pyxis_error(recv.params[0])

			self.__listen()
		except Exception as e:
			self.active = False
			pyxis_error(f"Disconnected due to {e}.")

		self.__disconnect()

if __name__ == "__main__":
	remote = Remote()
	remote.run()
	
