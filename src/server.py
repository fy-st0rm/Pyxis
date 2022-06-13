# pyxis api
from pyxis_api.pyxis_api   import *
from pyxis_api.util        import *
from pyxis_api.conf        import *
from pyxis_api.pyxis_types import *
from pyxis_api.pyxis_const import *

# Handlers
from pyxis_handlers.remote_handler import *
from pyxis_handlers.client_handler import *
from pyxis_database.pyxis_database import *


class Server:
	def __init__(self):
		self.__start_socket_server()
		self.__running = True

		# Handlers
		self.pyxis_database = Pyxis_Database()
		self.remote_handler = RemoteHandler(self.pyxis_database)
		self.client_handler = ClientHandler(self.pyxis_database)
		self.pyxis_database.remote_handler = self.remote_handler

	def __start_socket_server(self):
		try:
			self.server = socket.socket(SV_IP_TYPE, socket.SOCK_STREAM)
			self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.server.bind((IP, PORT))
		except Exception as e:
			pyxis_error(e)
			pyxis_error("Failed to start `pyxis server`.")
			exit(1)
	
	def __register_conn(self, conn):
		qry = pyxis_recv(conn)

		if qry.cmd != CONNECT:
			pyxis_send(conn, pQuery(qry.to, qry.by, FAILED, [f"`{qry.cmd}` is an invalid command. During the first connection the command should be `CONNECT [CLIENT/REMOTE]` only."], None))
			return 

		# Checking for which connection it is
		if qry.params[0] == REMOTE:
			self.remote_handler.add_new_remote(conn)
			pyxis_send(conn, pQuery(qry.to, qry.by, SUCESS, ["Sucessfully connected as remote."], None))

		elif qry.params[0] == CLIENT:
			self.client_handler.add_new_client(conn)
			pyxis_send(conn, pQuery(qry.to, qry.by, SUCESS, ["Sucessfully connected as client."], None))

		else:
			pyxis_send(conn, pQuery(qry.to, qry.by, FAILED, [f"Unknown type `{query.cmd}`. `CONNECT` has only two types `REMOTE/CLIENT`."], None))

	def __handle_connection(self, conn, addr):
		pyxis_sucess(f"{addr} connected.")
		self.__register_conn(conn)

		active = True
		while active:
			qry = pyxis_recv(conn)

			if qry.cmd == DISCONNECT:
				active = False
				pyxis_send(conn, pQuery(qry.to, qry.by, SUCESS, ["Sucessfully disconnected."], None))
				break

			if qry.to == CLI_HANDLER:
				res = self.client_handler.parse_query(conn, qry)
			elif qry.to == REM_HANDLER:
				res = self.remote_handler.parse_query(conn, qry)
			elif qry.to == PYX_DATABASE:
				pass
			else:
				res = pQuery(PYX_SERVER, qry.by, FAILED, [f"Command: {qry.cmd} doesnt exists."], None)

			pyxis_send(conn, res)

		pyxis_error(f"{addr} disconnected.")

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
