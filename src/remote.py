from pyxis_api.pyxis_api import *
from pyxis_api.util      import *
from pyxis_api.conf		 import *

class Remote:
	def __init__(self):
		self.api = Pyxis_API()
		self.queries = []
		self.__connect()

		self.running = True

	def __connect(self):
		query = pQuery(["CONNECT", "REMOTE"], None)
		self.api.query(query)
	
	def __store(self, data, pub_key):
		# Generating file name
		name = data.decode(FORMAT)
		name = name.split("]")[0].split("[")[1].strip(str(pub_key)) + str(uuid.uuid4())

		# TODO: Find the path to store the data
		# Storing data as tarfile
		params_sio = io.BytesIO(data)
		archive = tarfile.open(name + ".tgz", "w:gz")
		tarinfo = tarfile.TarInfo(name = name)
		tarinfo.size = len(data)
		archive.addfile(tarinfo, params_sio)
		archive.close()
	
	def __fetch(self, file, pub_key):
		pass
	
	def __listener(self):
		while self.running:
			# Getting the instructions from the remote handler
			recv = pyxis_recv(self.api.server)
			self.__parse_info(recv)
	
	def __parse_info(self, recv):
		if type(recv) == pQuery:
			self.__parse_query(recv)
		elif type(recv) == pResult:
			self.__parse_resut(recv)
		else:
			pyxis_error(f"Unknown type of data recevied\nTYPE: {type(recv)} DATA: {recv}")

	def __parse_resut(self, recv):
		if recv.sucess:
			pyxis_sucess(recv.log)
		else:
			pyxis_error(recv.log)

	def __parse_query(self, qry):
		# TODO: Exception handling here.
		# TODO: No feed back is given to the server so fix that

		if qry.cmd[0] == "STORE":
			self.__store(qry.cmd[1], qry.auth)
		elif qry.cmd[0] == "FETCH":
			self.__fetch(qry.cmd[1], qry.auth)

	def run(self):
		listen_thread = threading.Thread(target = self.__listener)
		listen_thread.start()

		file = input("Enter file path> ")
		with open(file, "rb") as r:
			data = r.read()

		if len(data) == 0:
			pyxis_warning("File empty.")
			exit(1)

		query = pQuery(["STORE", data], "123456789")
		self.api.query(query)
	

if __name__ == "__main__":
	remote = Remote()
	remote.run()
