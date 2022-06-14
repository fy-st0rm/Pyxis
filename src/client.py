# pyxis api
from pyxis_api.pyxis_types import *
from pyxis_api.pyxis_const import *
from pyxis_api.pyxis_api   import *

class Client:
	def __init__(self):
		self.api = Pyxis_API()

		self.name = "slok"
		self.pwd = "password"
		self.pub_key = None
	
	# Connect and Disconnect functions with pyxis server
	def __connect(self):
		qry = pQuery(CLIENT, PYX_SERVER, CONNECT, [CLIENT, self.name], self.pub_key)
		res = self.api.query(qry)
		if res.cmd == SUCESS:
			pyxis_sucess(res.params[0])
		else:
			pyxis_error(res.params[0])

	def __disconnect(self):
		qry = pQuery(CLIENT, PYX_SERVER, DISCONNECT, None, None)
		res = self.api.query(qry)
		if res.cmd == SUCESS:
			pyxis_sucess(res.params[0])
		else:
			pyxis_error(res.params[0])
			exit(1)

	def __login(self):
		qry = pQuery(CLIENT, CLI_HANDLER, LOGIN, [CLIENT, self.name], self.pwd)
		res = self.api.query(qry)
		if res.cmd == SUCESS:
			pyxis_sucess(res.params[0])
			self.pub_key = res.params[0]
		else:
			pyxis_error(res.params[0])
	
	def __signup(self):
		qry = pQuery(CLIENT, CLI_HANDLER, SIGNUP, [CLIENT, self.name], self.pwd)
		res = self.api.query(qry)
		if res.cmd == SUCESS:
			pyxis_sucess(res.params[0])
			self.pub_key = res.params[0]
		else:
			pyxis_error(res.params[0])

	# Store and fetch
	def __store(self):
		try:
			file = input("file> ")
			with open(os.path.join(file), "rb") as r:
				data = r.read()
			if len(data) <= 0:
				pyxis_error("File is empty")
				return
			
			pyxis_sucess(f"Sucessfully read file {file}")	
			qry = pQuery(CLIENT, PYX_DATABASE, STORE, [file.split("/")[1], data], self.pub_key)
			res = self.api.query(qry)

			if res.cmd == SUCESS:
				uid = res.params[0]
				pyxis_sucess(f"Sucessfully stored data in id: {uid}")
			elif res.cmd == FAILED:
				pyxis_error(res.params[0])
		except Exception as e:
			pyxis_error(e)

	def __fetch(self):
		uid = "fb58e4a4-a552-42a8-917f-30c503548222"
		qry = pQuery(CLIENT, PYX_DATABASE, FETCH, [uid], self.pub_key)
		res = self.api.query(qry)
		if res.cmd == SUCESS:
			pyxis_sucess(f"Sucessfully fetched file {res.params[0]}.")
			with open(res.params[0], "wb") as w:
				w.write(res.params[1])
			pyxis_sucess(f"Done storing.")
		else:
			pyxis_error(res.params[0])

	def run(self):
		self.__connect()
		self.__login()
		# self.__signup()

		self.__store()
		# self.__fetch()

		self.__disconnect()

if __name__ == "__main__":
	client = Client()
	client.run()
	
