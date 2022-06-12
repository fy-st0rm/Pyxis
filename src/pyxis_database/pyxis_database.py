# Pyxis api
from pyxis_api.conf		   import *
from pyxis_api.util 	   import *
from pyxis_api.pyxis_types import *
from pyxis_api.pyxis_const import *

# TODO: [ ] Maybe make database an independent server to increase mobility

class Pyxis_Database:
	def __init__(self):
		self.client_handler = None
		self.remote_handler = None
	
	def query(self, qry):
		# Parsing the query

		if len(qry.cmd) <= 1:
			return qResult("Database query command should have atleast one parameter.", None, False)

		if qry.cmd[0] == STORE:
			return self.__store(qry.cmd[1], qry.cmd[2], qry.auth)
		elif qry.cmd[0] == FETCH:
			return self.__fetch(qry.cmd[1], qry.auth)

	def __fetch(self, id, pub_key):
		pass

	def __store(self, file, data, pub_key):
		try:
			uid = uuid.uuid4() 
			remotes, remotes_no = self.remote_handler.get_remotes()

			# Adding a padding to make it properly chunkable
			n = remotes_no - len(data) % remotes_no
			data += b" " * n

			# Chunking the data
			chunk = {} 
			each = int(len(data) / remotes_no)
			chunk_no = 0
			for i in range(0, len(data), each):
				meta = f"[{uid}:{chunk_no}:{n}:{pub_key}]"
				name = meta.split("]")[0].split("[")[1].strip(str(pub_key)) + str(uuid.uuid4()).split("-")[0]
				chunk.update({name: meta.encode(FORMAT) + data[i:i+each]})
				chunk_no += 1

			# Sending the data to remote handler to distribute throuhout the network
			self.remote_handler.distribute_data(file, chunk, pub_key)

			pyxis_warning("##INFO##")
			pyxis_warning(f"Total chunks: {len(chunk)}")
			pyxis_warning(f"Total remotes: {remotes_no}")
			pyxis_sucess("Sucessfully distributed files.")
			return pResult("Sucessfully stored data.", [uid, remotes_no], True)
		except Exception as e:
			pyxis_error("Failed to distribute files.")
			return pResult(f"Failed to store data.\nReason: {e}", None, False)

