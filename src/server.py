# Pyxis apis
from pyxis_handlers.client_handler import *
from pyxis_handlers.remote_handler import *
from pyxis_database.pyxis_database import *

from pyxis_api.util          import *
from pyxis_api.pyxis_types   import *
from pyxis_api.conf			 import *
from pyxis_api.pyxis_const   import *


class Server:
	def __init__(self):
		self.database = Pyxis_Database()
		self.client_handler = ClientHandler(self.database)
		self.remote_handler = RemoteHandler(self.database)
		self.database.client_handler = self.client_handler
		self.database.remote_handler = self.remote_handler

		self.__start_socket_server()
		self.__running = True

	def __start_socket_server(self):
		try:
			self.server = socket.socket(SV_IP_TYPE, socket.SOCK_STREAM)
			self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.server.bind((IP, PORT))
		except Exception as e:
			pyxis_error(e)
			pyxis_error("Failed to start `pyxis server`.")
			exit(1)

	def __handle_connection(self, conn, addr):
		pyxis_sucess(f"{addr} has just connected.")

		# Parsing the query
		query = pyxis_recv(conn)

		# Checking if the command is connect or not. If not return.
		if query.cmd[0] != CONNECT:
			pyxis_send(conn, pResult(f"`{query.cmd[0]}` is an invalid command. During the first connection the command should be `CONNECT [CLIENT/REMOTE]` only.", None, False))
			return

		# Checking for which connection it is
		if query.cmd[1] == REMOTE:
			# Sucessfulling adding a new remote
			self.remote_handler.add_new_remote(conn, addr)
			pyxis_send(conn, pResult("Sucessfully connected as remote.", None, True))

		elif query.cmd[1] == CLIENT:
			pyxis_send(conn, pResult("Client handler hasnt been implemented yet.", None, False))

		else:
			pyxis_send(conn, pResult(f"Unknown type `{query.cmd[1]}`. `CONNECT` has only two types `REMOTE/CLIENT`.", None, False))
	
	def run(self):
		pyxis_sucess(f"Server has been started on {IP}.")
		self.server.listen()
		while self.__running:
			try:
				conn, addr = self.server.accept()

				thread = threading.Thread(target=self.__handle_connection, args=(conn, addr))
				thread.start()
			except KeyboardInterrupt:
				self.__running = False
		
		self.remote_handler.disconnect()
		pyxis_error(f"Shutting down server on {IP}.")

if __name__ == "__main__":
	server = Server()
	server.run()

