# Pyxis api
from pyxis_api.pyxis_api   import *
from pyxis_api.conf		   import *
from pyxis_api.pyxis_const import *

# TODO: Save the client database in a decentralized internet 

class ClientHandler:
	def __init__(self, database):
		self.database = database
		self.cli_data = {}
		self.clients = {}
		self.__load_cli_database()

	def add_new_client(self, conn):
		self.clients.update({conn: {"auth": False}})
	
	def __create_cli_database(self):
		if not os.path.exists(os.path.join("../client_data.json")):
			with open(os.path.join("../client_data.json"), "w") as w:
				w.write("{\n}")
			pyxis_sucess("Creating new client database.")
	
	def __load_cli_database(self):
		self.__create_cli_database()
		with open(os.path.join("../client_data.json"), "r") as r:
			self.cli_data = json.load(r)

	def __save_cli_database(self):
		with open(os.path.join("../client_data.json"), "w") as w:
			json.dump(self.cli_data, w, indent = 4)

	# Login and Signup functions
	def __login(self, conn, qry):
		name = qry.params[1]
		pwd  = qry.auth

		if name not in self.cli_data:
			return pQuery(CLI_HANDLER, qry.by, FAILED, [f"Username: {name} doesn't exists."], None)
	
		salt = self.cli_data[name]["salt"]
		pub_key =  str(hashlib.sha512((pwd + salt).encode()).hexdigest())

		if pub_key != self.cli_data[name]["pwd"]:
			return pQuery(CLI_HANDLER, qry.by, FAILED, [f"Incorrect password for user `{name}`."], None)
		
		self.clients[conn]["auth"] = True
		return pQuery(CLI_HANDLER, qry.by, SUCESS, [pub_key], None)

	def __signup(self, conn, qry):
		name = qry.params[1]
		pwd  = qry.auth

		if name in self.cli_data:
			return pQuery(CLI_HANDLER, qry.by, FAILED, [f"User with username `{name}` already exists. Please use another name."], None)

		salt =  str(uuid.uuid4())
		pub_key =  str(hashlib.sha512((pwd + salt).encode()).hexdigest())

		self.cli_data.update({name:{"salt": salt, "pwd": pub_key}})
		self.clients[conn]["auth"] = True

		self.__save_cli_database()
		return pQuery(CLI_HANDLER, qry.by, SUCESS, [pub_key], None)

	def parse_query(self, conn, qry):
		if qry.cmd == LOGIN:
			return self.__login(conn, qry)
		elif qry.cmd == SIGNUP:
			return self.__signup(conn, qry)
		else:
			return pQuery(qry.to, qry.by, FAILED, [f"Unknown `client handler` command: {qry.cmd}"], None)
