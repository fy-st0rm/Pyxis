import sys
import os
sys.path.append(os.path.abspath("../pyxis_api"))

from pyxis_api import *

FILE_NAME = "app_id.json"

class App_ID_Handler:
	def __init__(self):
		self.app_ids = {}
		self.__load_app_database()

	# Database handler
	def __create_app_database(self):
		if not os.path.exists(os.path.join(FILE_NAME)):
			with open(os.path.join(FILE_NAME), "w") as w:
				w.write("{\n}")
			pyxis_sucess("Creating new client database.")
	
	def __load_app_database(self):
		self.__create_app_database()
		with open(os.path.join(FILE_NAME), "r") as r:
			self.app_ids = json.load(r)

	def __save_app_database(self):
		with open(os.path.join(FILE_NAME), "w") as w:
			json.dump(self.app_ids, w, indent = 4)
	
	def check_app_id(self, app_id):
		if app_id in self.app_ids: return pQuery(SERVER, UNKNOWN, SUCESS, [f"valid app id: {app_id}."], None, uuid.uuid4())
		return pQuery(SERVER, UNKNOWN, FAILED, [f"Invalid app id: {app_id}."], None, uuid.uuid4())

