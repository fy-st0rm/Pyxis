from pyxis_api.pyxis_api     import *
from pyxis_api.util          import *
from pyxis_api.conf		     import *
from pyxis_api.pyxis_const   import *

class Remote:
	def __init__(self):
		self.api = Pyxis_API()
		self.__connect()

		self.running = True

	def __connect(self):
		query = pQuery([CONNECT, REMOTE], None)
		self.api.query(query)
	
	def __load_stored_data(self):
		data_register = []
		path = pyxis_get_storage_path(platform.system())
		files = os.listdir(path)

		for i in files:
			f_info = i.split(":")
			id     = f_info[0]
			chunk  = f_info[1]
			padd   = f_info[2]
			total  = f_info[3]
			file   = f_info[4]
			data_register.append((id, chunk, padd, total, file))

		return data_register
	
	# Submits the stored data information to the remote handler
	def __submit_register(self):
		data_register = self.__load_stored_data()
		self.api.query(pQuery([DATA, data_register], None))
	
	# Database functions
	def __load_zip(self, path, file, pub_key):
		with pyzipper.AESZipFile(path + file) as zf:
			zf.setpassword(pub_key)
			data = zf.read(file.strip(".zip"))
		return data

	def __store(self, data, pub_key):
		# Getting the path to store data
		file = data[0]
		name = data[1]
		data = data[2]
		path = pyxis_get_storage_path(platform.system())

		pyxis_sucess("Compressing and encrypting.")
		with pyzipper.AESZipFile(path + name + ".zip", "w", compression=pyzipper.ZIP_LZMA, encryption=pyzipper.WZ_AES) as zf:
			zf.setpassword(pub_key)
			zf.writestr(name, data)
		pyxis_sucess("Sucessfully stored data.")
	
	def __fetch(self, file, pub_key):
		uid = file[0]
		idx = file[1]

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
					res = pResult(f"Sucessfully extracted the file {uid}:{idx}.", data, True)
					self.api.query(res)
				except Exception as e:
					print(e)
					res = pResult(f"Error fetching: {e}", None, False)
					self.api.query(res)
	
	def __download(self, info):
		file = info[0]
		data = info[1]

		with open(file, "wb") as w:
			w.write(data)

		pyxis_sucess(f"Sucessfully downloaded file {file}.")

	# Parsers
	def __parse_resut(self, recv):
		if recv.log == DATA_STORED:
			id = recv.data[0]
			pyxis_sucess(f"Data stored in id: {id}")

		if not recv.sucess:
			pyxis_error(recv.log)

	def __parse_query(self, qry):
		if qry.cmd[0] == STORE:
			threading.Thread(target = self.__store, args = (qry.cmd[1], qry.auth)).start()

		elif qry.cmd[0] == FETCH:
			print(qry.cmd[1])
			self.__fetch(qry.cmd[1], qry.auth)

		elif qry.cmd[0] == DOWNLOAD:
			self.__download(qry.cmd[1])

		elif qry.cmd[0] == DISCONNECT:
			self.running = False
			self.api.server.close()
			pyxis_error("Remote has been disconnected.")

	def __parse_info(self, recv):
		if type(recv) == pQuery:
			self.__parse_query(recv)
		elif type(recv) == pResult:
			self.__parse_resut(recv)
		else:
			pyxis_error(f"Unknown type of data recevied\nTYPE: {type(recv)} DATA: {recv}")

	# Listener
	def __listener(self):
		while self.running:
			# Getting the instructions from the remote handler
			recv = pyxis_recv(self.api.server)
			self.__parse_info(recv)

	def run(self):
		listen_thread = threading.Thread(target = self.__listener)
		listen_thread.start()

		# Sending the stored data indices to the remote handler
		self.__submit_register()

		# File storing test
		# file = input("File> ")
		# with open(os.path.join(file), "rb") as r:
		# 	data = r.read()
		# 
		# if (len(data) == 0):
		# 	exit(1)

		# pyxis_sucess(f"Sucessfully read file {file}.")
		# qry = pQuery([STORE, file.split("/")[1], data], b"password")
		# self.api.query(qry)

		# File fetching test
		input("Start")
		qry = pQuery([FETCH, "8a13bda8-f3aa-4de1-8bc6-57e2862249b9"], b"password")
		self.api.query(qry)

if __name__ == "__main__":
	remote = Remote()
	remote.run()
