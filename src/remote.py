from pyxis_api.pyxis_api import *
from pyxis_api.util      import *
from pyxis_api.conf		 import *

class Remote:
	def __init__(self):
		self.api = Pyxis_API()
		self.__connect()

		self.running = True
	
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
			time.sleep(DELAY)

			# Getting the instructions from the remote handler
			query = pickle.loads(self.api.server.recv(BUFF_CAP))
			self.query(query)
	
	def __connect(self):
		query = pQuery(["CONNECT", "REMOTE"], None)
		res = self.api.query(query)
		if res.sucess:
			pyxis_sucess(res.log)
		else:
			pyxis_error(res.log)
			exit(1)

	def query(self, qry):
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
		query = pQuery(["STORE", data], "123456789")
		self.api.query(query)
	

if __name__ == "__main__":
	remote = Remote()
	remote.run()
