import sys
import os
sys.path.append(os.path.abspath("../pyxis_api"))

from pyxis_api import *
from cli_handler import *


class Server:
	def __init__(self, ip, port):
		self.ip = ip 
		self.port = port 
		self.sv_addr = (self.ip, self.port)
		self.__create_server()

		# address = {
		#       user_id: ip address,
		#       ....
		# }
		self.address = {}
		self.running = True

		# Handlers
		self.cli_handler = Cli_Handler(self)

	def __create_server(self):
		try:
			self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.server.bind((self.ip, self.port))
			pyxis_sucess(f"Server hosted on {self.ip}:{self.port}")
		except Exception as e:
			pyxis_error(e)
			exit()

	def __distribute_addr(self):
		for user in self.address:
			addr = self.address[user]
			qry = pQuery(self.sv_addr, addr, PEERS_ADDR, self.address, uuid.uuid4())
			pyxis_send(self.server, qry)

	# Server query handler
	def __handler(self, data, addr):
		if data.cmd == SIGNUP or data.cmd == LOGIN:
			result = self.cli_handler.parse_query(data, addr)
		else:
			result = pQuery(self.sv_addr, addr, FAILED, [f"Unknown command `{data.cmd}`."], None)
		
		result.by  = self.sv_addr
		result.to  = data.by
		result.pid = data.pid
		pyxis_send(self.server, result)

	def run(self):
		while self.running:
			data, addr = pyxis_recv(self.server)

			if data.cmd == CONNECT:
				if data.params[0] in self.address:
					pyxis_sucess(f"{addr} connected.")
					qry = pQuery(self.sv_addr, addr, SUCESS, [f"Sucessfully connected to server."], data.pid)
					pyxis_send(self.server, qry)
					self.__distribute_addr()
				else:
					pyxis_error(f"{addr} failed to connect.")
					qry = pQuery(self.sv_addr, addr, FAILED, [f"Cannot connect to server without authenticating. `Login` or `Signup` for authentication."], data.pid)
					pyxis_send(self.server, qry)


			# When client disconnects
			elif data.cmd == DISCONNECT:
				if data.params[0] in self.address: self.address.pop(data.params[0])
				self.__distribute_addr()
				pyxis_error(f"{addr} disconnected.")

			else:
				threading.Thread(target = self.__handler, args = (data, addr)).start()

if __name__ == "__main__":
	sv = Server(socket.gethostbyname(socket.gethostname()), 6969)
	sv.run()
