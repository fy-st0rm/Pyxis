# pyxis api
from pyxis_api.pyxis_types import *
from pyxis_api.pyxis_const import *
from pyxis_api.pyxis_api   import *

class Remote:
	def __init__(self):
		self.api = Pyxis_API()
	
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
		res = self.api.query(qry)
		if res.cmd == SUCESS:
			pyxis_sucess(res.params[0])
		else:
			pyxis_error(res.params[0])
			exit(1)
	
	# Storing and fetching
	def __load_zip(self, path, file, pub_key):
		with pyzipper.AESZipFile(path + file) as zf:
			zf.setpassword(pub_key)
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

			return pQuery(REMOTE, REM_HANDLER, STORED, [f"Sucessfully stored in remote."], None)
		except Exception as e:
			return pQuery(REMOTE, REM_HANDLER, STORED_FAILED, [f"Failed to store in remote.\nReason: {e}"], None)

	def __fetch(self, qry):
		uid = qry.params[0]
		idx = qry.params[1]
		pub_key = qry.auth.encode()

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
					res = pQuery(REMOTE, REM_HANDLER, FETCHED, [uid, idx, pub_key.decode(), data], None)
					return res

				except Exception as e:
					res = pQuery(REMOTE, REM_HANDLER, FETCHED_FAILED, [uid, f"Error fetching from remote.\nReason: {e}"], None)
					return res

		return pQuery(REMOTE, REM_HANDLER, FETCHED_FAILED, [uid, f"File with uid: {uid} and chunk: {idx} is not located in this remote."], None)
	
	# Listener for remote handler
	def __listen(self):
		active = True
		while active:
			recv = pyxis_recv(self.api.server)
			if recv.cmd == STORE:
				res = self.__store(recv)
				pyxis_send(self.api.server, res)
			elif recv.cmd == FETCH:
				res = self.__fetch(recv)
				pyxis_send(self.api.server, res)
	
	def run(self):
		try:
			self.__connect()
			self.__register_data()
			self.__listen()
		except:
			pass

		self.__disconnect()

if __name__ == "__main__":
	remote = Remote()
	remote.run()
	
