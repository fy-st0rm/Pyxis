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
		if qry.cmd == STORE and len(qry.params) != 2:
			return pQuery(PYX_DATABASE, qry.by, FAILED, [f"{qry.cmd} requires two arguments."], None)

		if not self.client_handler.clients[conn]["auth"]:
			return pQuery(PYX_DATABASE, qry.by, FAILED, [f"Client hasnt been authenticated yet. Run `LOGIN` or `SIGNUP` command to authenticate your connection."], None)

		if qry.cmd == STORE:
			return self.__store(qry)
		elif qry.cmd == FETCH:
			return self.__fetch(qry)
		elif qry.cmd == DELETE:
			return self.__delete(qry)
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
			self.remote_handler.distribute_data(chunks, pub_key)
			recv = self.remote_handler.get_result(STORE, pub_key)
			if recv.cmd == FAILED:
				raise Exception (recv.params[0])

			pyxis_warning("##DATA STORED INFO##")
			pyxis_warning(f"Total chunks: {chunk_no}")
			pyxis_warning(f"Total remotes: {remotes_no}")

			return pQuery(PYX_DATABASE, qry.by, SUCESS, [uid, remotes_no], None)

		except Exception as e:
			pyxis_error("Failed to distribute files.")
			return pQuery(PYX_DATABASE, qry.by, FAILED, [f"Failed to store data.\nReason: {e}"], None)

	def __fetch(self, qry):
		try:
			uid = qry.params[0]
			if uid not in self.remote_handler.data_register:
				raise Exception(f"{uid} is an invalid uid. Cannot found in database.")

			# Asking for remote handler to fetch the datas
			self.remote_handler.fetch_data(uid, qry.auth)
			recv = self.remote_handler.retrive_fetched_data(uid, qry.auth)
			
			if recv.cmd == FAILED:
				raise Exception(recv.params[0])

			reg = self.remote_handler.data_register[uid]
			file  = reg["file"]
			padd  = int(reg["padd"])
			total = int(reg["total"])
			chunks = recv.params

			data = b""
			for i in chunks:
				data += i
			data.strip(b" " * padd)

			return pQuery(PYX_DATABASE, qry.by, SUCESS, [file, data], None)

		except Exception as e:
			pyxis_error(f"Failed to fetch file.\nReason: {e}")
			return pQuery(PYX_DATABASE, qry.by, FAILED, [f"Failed to fetch file.\nReason: {e}"], None)
	
	def __delete(self, qry):
		try:
			uid = qry.params[0]
			if uid not in self.remote_handler.data_register:
				raise Exception(f"{uid} is an invalid uid. Cannot found in database.")

			self.remote_handler.delete_data(uid, qry.auth)
			recv = self.remote_handler.get_result(DELETE, qry.auth)
			if recv.cmd == FAILED:
				raise Exception(recv.params[0])

			return pQuery(PYX_DATABASE, qry.by, SUCESS, [f"Sucessfully deleted file with uid {uid}."], None)

		except Exception as e:
			pyxis_error(f"Failed to delete file.\nReason: {e}")
			return pQuery(PYX_DATABASE, qry.by, FAILED, [f"Failed to delete file.\nReason: {e}"], None)

