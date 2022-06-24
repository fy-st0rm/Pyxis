# pyxis api
from pyxis_api.pyxis_types import *
from pyxis_api.pyxis_const import *
from pyxis_api.pyxis_api   import *

class Client:
	def __init__(self):
		self.api = Pyxis_API()
		self.name = None
		self.pwd = None
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
		self.name = input("Username: ")
		self.pwd  = input("Password: ")
		qry = pQuery(CLIENT, CLI_HANDLER, LOGIN, [CLIENT, self.name], self.pwd)
		res = self.api.query(qry)
		if res.cmd == SUCESS:
			pyxis_sucess(f"Sucessfully logged in with pub_key: {res.params[0]}")
			self.pub_key = res.params[0]
		else:
			pyxis_error(res.params[0])
			raise Exception(res.params[0])
	
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
				self.uid = res.params[0]
				pyxis_sucess(f"Sucessfully stored data in id: {self.uid}")
			elif res.cmd == FAILED:
				pyxis_error(res.params[0])
		except Exception as e:
			pyxis_error(e)

	def __fetch(self):
		uid = "befc0fe8-0d58-4656-960d-17b5084ffb16"
		qry = pQuery(CLIENT, PYX_DATABASE, FETCH, [self.uid], self.pub_key)
		res = self.api.query(qry)
		if res.cmd == SUCESS:
			pyxis_sucess(f"Sucessfully fetched file {res.params[0]}.")
			with open(res.params[0], "wb") as w:
				w.write(res.params[1])
			pyxis_sucess(f"Done storing.")
		else:
			pyxis_error(res.params[0])
	
	def __delete(self):
		uid = "72205d51-4de7-494d-96b8-70562a1c27bc"
		qry = pQuery(CLIENT, PYX_DATABASE, DELETE, [self.uid], self.pub_key)
		res = self.api.query(qry)
		if res.cmd == SUCESS:
			pyxis_sucess(res.params[0])
		else:
			pyxis_error(res.params[0])
	
	def __replace(self):
		uid = "befc0fe8-0d58-4656-960d-17b5084ffb16"
		qry = pQuery(CLIENT, PYX_DATABASE, REPLACE, [self.uid, b"Hello everyone"], self.pub_key)
		res = self.api.query(qry)
		if res.cmd == SUCESS:
			pyxis_sucess(res.params[0])
		else:
			pyxis_error(res.params[0])

	def run(self):
		a = 2
		try:
			self.__connect()
			self.__login()
			# self.__signup()

			pyxis_warning("testing: STORE")
			self.__store()
			time.sleep(a)
			pyxis_warning("testing: FETCH")
			self.__fetch()
			time.sleep(a)
			pyxis_warning("testing: REPLACE")
			self.__replace()
			time.sleep(a)
			pyxis_warning("testing: FETCH")
			self.__fetch()
			time.sleep(a)
			pyxis_warning("testing: DELETE")
			self.__delete()
			time.sleep(a)
			pyxis_warning("testing: FETCH")
			self.__fetch()
			time.sleep(a)
		except Exception as e:
			pyxis_error(f"Disconnected due to: {e}")

		self.__disconnect()

if __name__ == "__main__":
	client = Client()
	client.run()
	
