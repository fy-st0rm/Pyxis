import sys
import os
sys.path.append(os.path.abspath("../pyxis_api"))

from pyxis_api import *
from cli_handler import *
from app_id_handler import *

class Server:
	def __init__(self, ip, port):
		self.ip = ip 
		self.port = port 
		self.__create_server()

		self.address = []
		self.running = True

		# Handlers
		self.cli_handler = Cli_Handler()
		self.app_id_handler = App_ID_Handler()	

	def __create_server(self):
		try:
			self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.server.bind((self.ip, self.port))
			pyxis_sucess(f"Server hosted on {self.ip}:{self.port}")
		except Exception as e:
			pyxis_error(e)
			exit()

	def __distribute_addr(self):
		for addr in self.address:
			qry = pQuery(SERVER, UNKNOWN, PEERS_ADDR, self.address, None, uuid.uuid4())
			pyxis_send(self.server, addr, qry)

	# Server query handler
	def __handler(self, data, addr):
		result = self.app_id_handler.check_app_id(data.app_id)
		
		if result.cmd == SUCESS:
			if data.cmd == SIGNUP or data.cmd == LOGIN:
				result = self.cli_handler.parse_query(data)
		
		result.pid = data.pid
		pyxis_send(self.server, addr, result)

	def run(self):
		while self.running:
			data, addr = pyxis_recv(self.server)

			# When we first connect
			if data.cmd == CONNECT:
				pyxis_sucess(f"{addr} connected.")
				if addr not in self.address: self.address.append(addr)
				self.__distribute_addr()

			# When client disconnects
			elif data.cmd == DISCONNECT:
				if addr in self.address: self.address.remove(addr)
				self.__distribute_addr()
				pyxis_error(f"{addr} disconnected.")
			else:
				threading.Thread(target = self.__handler, args = (data, addr)).start()

if __name__ == "__main__":
	sv = Server(socket.gethostbyname(socket.gethostname()), 6969)
	sv.run()
