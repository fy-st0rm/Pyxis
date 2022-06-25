import sys
import os
sys.path.append(os.path.abspath("../pyxis_api"))
from pyxis_api import *

FILE_NAME = "client_data.json" 

class Cli_Handler:
	def __init__(self, server):
		# {
		#     "name": {
		#                 "uid": Unique identifier of the user,
		#				  "salt": Salt of the hash,
		#                 "pwd": Hased password,
		#              },
		#     ....
		# }
		self.cli_data = {}
		self.server = server
		self.__load_cli_database()
	
	# Database handler
	def __create_cli_database(self):
		if not os.path.exists(os.path.join(FILE_NAME)):
			with open(os.path.join(FILE_NAME), "w") as w:
				w.write("{\n}")
			pyxis_sucess("Creating new client database.")
	
	def __load_cli_database(self):
		self.__create_cli_database()
		with open(os.path.join(FILE_NAME), "r") as r:
			self.cli_data = json.load(r)

	def __save_cli_database(self):
		with open(os.path.join(FILE_NAME), "w") as w:
			json.dump(self.cli_data, w, indent = 4)

	# Authentication handler
	def user_authenticated(self, user_uuid, addr):
		if user_uuid not in self.server.address:
			self.server.address.update({user_uuid: addr})
			return True
		return False

	def signup(self, username, password, addr):
		if username in self.cli_data: return pQuery(SERVER, UNKNOWN, FAILED, [f"Username `{username}` already exists. Please choose another one."], uuid.uuid4())
		
		# Generating user uuid
		user_uuid = str(hashlib.sha512(username.encode()).hexdigest())

		# Generating hash
		salt = str(uuid.uuid4())
		hashed = str(hashlib.sha512((password + salt).encode()).hexdigest())
			
		# Appending it to the database
		self.cli_data.update({username: {"uid": user_uuid, "salt": salt, "pwd": hashed}})
		self.__save_cli_database()

		res = self.user_authenticated(user_uuid, addr)
		if not res: return pQuery(SERVER, UNKNOWN, FAILED, [f"User `{username}` is already online."], uuid.uuid4())

		return pQuery(SERVER, UNKNOWN, SUCESS, [f"Sucessfully created a new account.", user_uuid, hashed], uuid.uuid4())

	def login(self, username, password, addr):
		if username not in self.cli_data: return pQuery(SERVER, UNKNOWN, FAILED, [f"User with username `{username}` doesn`t exists."], uuid.uuid4())

		# Gathering the info from database
		user_uuid = self.cli_data[username]["uid"]
		salt      = self.cli_data[username]["salt"]
		hashed    = self.cli_data[username]["pwd"]

		# Checking the password
		supplied_hashed = str(hashlib.sha512((password + salt).encode()).hexdigest())
		if supplied_hashed != hashed: return pQuery(SERVER, UNKNOWN, FAILED, [f"Password for user `{username}` didn`t matched."], uuid.uuid4())

		res = self.user_authenticated(user_uuid, addr)
		if not res: return pQuery(SERVER, UNKNOWN, FAILED, [f"User `{username}` is already online."], uuid.uuid4())

		return pQuery(SERVER, UNKNOWN, SUCESS, [f"Sucessfully logged in.", user_uuid, hashed], uuid.uuid4())
	
	# Query Handler
	def parse_query(self, qry, addr):
		if   qry.cmd == SIGNUP: return self.signup(qry.params[0], qry.params[1], addr)
		elif qry.cmd == LOGIN : return self.login(qry.params[0], qry.params[1], addr)

