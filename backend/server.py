from client_handler import *
from remote_handler import *
from database		import *


class Server:
	def __init__(self):
		self.database = Database()
		self.client_handler = ClientHandler(self.database)
		self.remote_handler = RemoteHandler(self.database)
		self.database.handler = self.remote_handler
	
	def run(self):
		pass

if __name__ == "__main__":
	server = Server()
	server.run()

