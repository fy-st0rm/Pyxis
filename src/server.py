# Pyxis apis
from handlers.client_handler import *
from handlers.remote_handler import *
from database.database       import *

from pyxis_api.util          import *
from pyxis_api.pyxis_types   import *
from pyxis_api.conf			 import *

# Standard python
import threading


class Server:
	def __init__(self):
		self.database = Database()
		self.client_handler = ClientHandler(self.database)
		self.remote_handler = RemoteHandler(self.database)
		self.database.handler = self.remote_handler

		self.__start_socket_server()
		self.__running = True

	def __start_socket_server(self):
		try:
			self.server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
			self.server.bind((IPv6, PORT))
		except Exception as e:
			pyxis_error(e)
			pyxis_error("Failed to start `pyxis server`.")
			exit(1)

	def __handle_connection(self, conn, addr):
		pyxis_sucess(f"{addr} has just connected.")

		# Parsing the query
		query = pickle.loads(conn.recv(BUFF_CAP))

		# Checking if the command is connect or not. If not return.
		if query.cmd[0] != "CONNECT":
			conn.send(pickle.dumps(pResult(f"`{query.cmd[0]}` is an invalid command. During the first connection the command should be `CONNECT [CLIENT/REMOTE]` only.", None, False)))
			return

		# Checking for which connection it is
		if query.cmd[1] == "REMOTE":
			# Sucessfulling adding a new remote
			self.remote_handler.add_new_remote(conn, addr)
			conn.send(pickle.dumps(pResult("Sucessfully connected as remote.", None, True)))

		elif query.cmd[1] == "CLIENT":
			conn.send(pickle.dumps(pResult("Client handler hasn`t been implemented yet.", None, False)))

		else:
			conn.send(pickle.dumps(pResult(f"Unknown type `{query.cmd[1]}`. `CONNECT` has only two types `REMOTE/CLIENT`.", None, False)))

		# pyxis_warning(f"{addr} has just disconnected.")
	
	def run(self):
		self.server.listen()
		while self.__running:
			conn, addr = self.server.accept()

			thread = threading.Thread(target=self.__handle_connection, args=(conn, addr))
			thread.start()

if __name__ == "__main__":
	server = Server()
	server.run()
