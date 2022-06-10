# Pyxis api
from pyxis_api.pyxis_api import *
from pyxis_api.conf		 import *

class RemoteHandler:
	def __init__(self, database):
		self.database = database
		self.remotes = {}
	
	def __handle_remote(self, conn, addr):
		active = True
		while active:
			pass

		self.remotes.pop(addr)

	def add_new_remote(self, conn, addr):
		self.remotes.update({addr, conn})
		thread = threading.Thread(target = self.__handle_remote, args = (conn, addr))
		thread.start()
