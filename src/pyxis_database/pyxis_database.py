# Pyxis api
from pyxis_api.conf		   import *
from pyxis_api.util 	   import *
from pyxis_api.pyxis_types import *

# TODO: [ ] Maybe make database an independent server to increase mobility

class Pyxis_Database:
	def __init__(self):
		self.client_handler = None
		self.remote_handler = None
	
	def query(self, qry):
		# Parsing the query

		if len(qry.cmd) <= 1:
			return qResult("Database query command should have atleast one parameter.", None, False)

		if qry.cmd[0] == "STORE":
			return self.__store(qry.cmd[1], qry.auth)
		elif qry.cmd[0] == "FETCH":
			return self.__fetch(qry.cmd[1], qry.auth)

	def __fetch(self, id, pub_key):
		pass

	def __store(self, data, pub_key):
		uid = uuid.uuid4() 
		remotes, remotes_no = self.remote_handler.get_remotes()

		# Adding a padding to make it properly chunkable
		n = remotes_no - len(data) % remotes_no
		data += b" " * n

		# Chunking the data
		chunk = []
		each = int(len(data) / remotes_no)
		for i in range(remotes_no):
			meta = f"[{uid}:{i}:{n}:{pub_key}]".encode(FORMAT)
			chunk.append(meta + data[i:i+each])
		
		# Dublicating data
		for i in range(DATA_DUPLICATION_AMT):
			chunk += chunk

		# Shuffling the data
		random.shuffle(chunk)

		# Sending the data to remote handler to distribute throuhout the network
		self.remote_handler.distribute_data(chunk, pub_key)

		pyxis_warning("##INFO##")
		pyxis_warning(f"Total chunks: {len(chunk)}")
		pyxis_warning(f"Total remotes: {remotes_no}")
		pyxis_warning(f"sizeof data avg: {sys.getsizeof(chunk[0])}")

