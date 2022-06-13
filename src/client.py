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


	def run(self):
		self.__connect()
		self.__login()
		# self.__signup()
		self.__disconnect()

if __name__ == "__main__":
	client = Client()
	client.run()
	
