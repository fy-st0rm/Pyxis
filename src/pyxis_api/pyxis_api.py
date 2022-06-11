# Pyxis apis'
from pyxis_api.util        import *
from pyxis_api.pyxis_types import *
from pyxis_api.conf		   import *


class Pyxis_API:
	def __init__(self):
		self.sv_ip = IP
		self.sv_port = 6969

		self.__connect()

	def __connect(self):
		try:
			self.server = socket.socket(SV_IP_TYPE, socket.SOCK_STREAM)
			self.server.connect((self.sv_ip, self.sv_port))
		except Exception as e:
			pyxis_error(e)
			pyxis_error("Failed to connect to `pyxis server`.")
			exit(1)
	
	def query(self, qry):
		pyxis_send(self.server, qry)

