import sys
import os
sys.path.append(os.path.abspath("pyxis_api"))
from pyxis_api import *

class App:
	def __init__(self):
		self.api = Pyxis_API()
		self.app_id = "3052f9bd-0b76-4ec7-b0dc-0858d18f43b5"
		self.usr_id = None
		self.pub_key = None
		
	def __login(self):
		username = input("Username: ")
		pwd = input("Password: ")
		result = self.api.login(username, pwd, self.app_id)

		if result["result"] == SUCESS:
			pyxis_sucess(result["log"])
			self.usr_id, self.pub_key = result["values"][0].params
		else:
			pyxis_error(result["log"])
			self.close()

	def __signup(self):
		username = input("Username: ")
		pwd = input("Password: ")
		result = self.api.signup(username, pwd, self.app_id)
		if result["result"] == SUCESS:
			pyxis_sucess(result["log"])
			self.usr_id, self.pub_key = result["values"][0].params
		else:
			pyxis_error(result["log"])
			self.close()
	
	def listener(self, qry):
		if qry.cmd == "msg":
			print("\rpeer>", qry.params[0])

	def run(self):
		try:
			self.api.set_listener(self.listener)

			# self.__signup()
			self.__login()

			pyxis_sucess(f"Userid: {self.usr_id}, PubKey: {self.pub_key}")

			while True:
				text = input(f"{Colors.YELLOW}You> {Colors.DEFAULT}")
				qry = pQuery(self.usr_id, UNKNOWN, "msg", [text], self.app_id, None)
				pid = self.api.query(qry)

		except KeyboardInterrupt as e:
			pyxis_error(e)
	
	def close(self):
		self.api.close()

if __name__ == "__main__":
	app = App()
	app.run()
	app.close()

