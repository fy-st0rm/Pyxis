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
	
	def __store(self, data, pub_key):
		# Getting the path to store data
		file = data[0]
		name = data[1]
		data = data[2]
		path = pyxis_get_storage_path(platform.system())

		with pyzipper.AESZipFile(path + name + ".zip", "w", compression=pyzipper.ZIP_LZMA, encryption=pyzipper.WZ_AES) as zf:
			zf.setpassword(pub_key.encode(FORMAT))
			zf.writestr(name, data)
		pyxis_sucess("Finished storing.")
	
	def __fetch(self, file, pub_key):
		pass

	def __parse_resut(self, recv):
		if recv.sucess:
			pyxis_sucess(recv.log)
		else:
			pyxis_error(recv.log)

	def __parse_query(self, qry):
		# TODO: Exception handling here.
		if qry.cmd[0] == STORE:
			self.__store(qry.cmd[1], qry.auth)
		elif qry.cmd[0] == FETCH:
			self.__fetch(qry.cmd[1], qry.auth)
		elif qry.cmd[0] == DISCONNECT:
			self.running = False
			pyxis_error("Remote has been disconnected.")

	def __parse_info(self, recv):
		if type(recv) == pQuery:
			self.__parse_query(recv)
		elif type(recv) == pResult:
			self.__parse_resut(recv)
		else:
			pyxis_error(f"Unknown type of data recevied\nTYPE: {type(recv)} DATA: {recv}")

	def __listener(self):
		while self.running:
			# Getting the instructions from the remote handler
			recv = pyxis_recv(self.api.server)
			self.__parse_info(recv)

	def run(self):
		listen_thread = threading.Thread(target = self.__listener)
		listen_thread.start()

		file = input("File> ")
		with open(os.path.join(file), "rb") as r:
			data = r.read()
		
		if (len(data) == 0):
			exit(1)

		pyxis_sucess(f"Sucessfully read file {file}.")
		qry = pQuery([STORE, file.split("/")[1], data], "password")
		self.api.query(qry)

if __name__ == "__main__":
	remote = Remote()
	remote.run()
