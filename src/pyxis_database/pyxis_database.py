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
		pass
