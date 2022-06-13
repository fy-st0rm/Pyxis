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
	
	def parse_query(self, conn, qry):
		if len(qry.params) != 2:
			return pQuery(PYX_DATABASE, qry.by, FAILED, [f"{qry.cmd} requires two arguments."], None)

		if qry.cmd == STORE:
			return self.__store(qry)
		elif qry.cmd == FETCH:
			return self.__fetch(qry.params, qry.auth)
		else:
			return pQuery(PYX_DATABASE, qry.by, FAILED, [f"Unknown `Pyxis database` command {qry.cmd}."], None)

	def __store(self, qry):
		try:
			file = qry.params[0]
			data = qry.params[1]
			pub_key = qry.auth

			uid = uuid.uuid4() 
			remotes, remotes_no = self.remote_handler.get_remotes()

			# Adding a padding to make it properly chunkable
			padd = remotes_no - len(data) % remotes_no
			data += b" " * padd

			# Chunking the data
			chunks = {} 
			each = int(len(data) / remotes_no)
			chunk_no = 0
			for i in range(0, len(data), each):
				name = f"{uid}:{chunk_no}:{padd}:{remotes_no}:{file}:" + str(uuid.uuid4()).split("-")[0]
				chunks.update({name: data[i:i+each]})
				chunk_no += 1

			# Sending the data to remote handler to distribute throuhout the network
			res = self.remote_handler.distribute_data(chunks, pub_key)
			if res.cmd == FAILED:
				raise Exception(res.params[0])
			
			pyxis_warning("##DATA STORED INFO##")
			pyxis_warning(f"Total chunks: {chunk_no}")
			pyxis_warning(f"Total remotes: {remotes_no}")

			return pQuery(PYX_DATABASE, qry.by, SUCESS, [uid, remotes_no], None)

		except Exception as e:
			pyxis_error("Failed to distribute files.")
			return pQuery(PYX_DATABASE, qry.by, FAILED, [f"Failed to store data.\nReason: {e}"], None)

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

