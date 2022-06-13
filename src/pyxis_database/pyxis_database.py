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

	def __fetch(self, uid, pub_key):
		try:
			if uid not in self.remote_handler.data_register:
				raise Exception(f"{uid} is an invalid uid. Cannot found in database.")

			reg = self.remote_handler.data_register[uid]
			file  = reg["file"]
			padd  = int(reg["padd"])
			total = int(reg["total"])

			final_data = b""
			for i in range(total):
				conn = random.choice(reg[str(i)])
				print(conn)
				pyxis_send(conn, pQuery([FETCH, (uid, str(i))], pub_key))
				recv = pyxis_recv(conn)
				print(recv.log, recv.data)

				if not recv.sucess:
					raise Exception(recv.log)

				pyxis_sucess(recv.log)
				final_data += recv.data

			pyxis_sucess(f"Sucessfully retreived the file with id: {uid}")
			return pQuery([DOWNLOAD, [file, final_data]], None)

		except Exception as e:
			pyxis_error(f"Failed to fetch file.\nReason: {e}")
			return pResult(f"Failed to fetch file.\nReason: {e}", None, False)

	def __store(self, file, data, pub_key):
		try:
			uid = uuid.uuid4() 
			remotes, remotes_no = self.remote_handler.get_remotes()

			# Adding a padding to make it properly chunkable
			padd = remotes_no - len(data) % remotes_no
			data += b" " * padd

			# Chunking the data
			chunk = {} 
			each = int(len(data) / remotes_no)
			chunk_no = 0
			for i in range(0, len(data), each):
				name = f"{uid}:{chunk_no}:{padd}:{remotes_no}:{file}:" + str(uuid.uuid4()).split("-")[0]
				chunk.update({name: data[i:i+each]})
				chunk_no += 1

			# Sending the data to remote handler to distribute throuhout the network
			self.remote_handler.distribute_data(file, chunk, pub_key)
			
			pyxis_warning("##DATA STORED INFO##")
			pyxis_warning(f"Total chunks: {len(chunk)}")
			pyxis_warning(f"Total remotes: {remotes_no}")
			return pResult(DATA_STORED, [uid, remotes_no], True)

		except Exception as e:
			pyxis_error("Failed to distribute files.")
			return pResult(f"Failed to store data.\nReason: {e}", None, False)

