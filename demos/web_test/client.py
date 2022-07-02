import sys
import os
sys.path.append(os.path.abspath("../../pyxis_api"))
from pyxis_api import *
import eel

class App:
	def __init__(self):
		self.api = Pyxis_API()
		self.usr_id = None
		self.pub_key = None
		
	def login(self, username, pwd):
		result = self.api.login(username, pwd)

		if result.result == SUCESS:
			pyxis_sucess(result.log)
			eel.main_page()
			self.usr_id, self.pub_key = result.values[0].params
		else:
			eel.notify(result.log)
			pyxis_error(result.log)

	def signup(self, username, pwd):
		result = self.api.signup(username, pwd)

		if result.result == SUCESS:
			pyxis_sucess(result.log)
			eel.notify(result.log)
			eel.main_page()
			self.usr_id, self.pub_key = result.values[0].params
		else:
			eel.notify(result.log)
			pyxis_error(result.log)

	def connect(self):
		qry = pQuery(self.api.addr, self.api.sv_addr, CONNECT, [self.usr_id], None)
		pid = self.api.query(qry)
		res = self.api.process_handler.get_process_result(pid)
		if res.result == SUCESS:
			pyxis_sucess(res.log)
		else:
			pyxis_error(res.log)

	def listener(self, qry, addr):
		if qry.cmd == "msg":
			print("\rpeer>", qry.params[0])

	def run(self):
		try:
			while True:
				text = input(f"{Colors.YELLOW}You> {Colors.DEFAULT}")
				for i in self.api.peers:
					if i != self.usr_id:
						qry = pQuery(self.api.addr, self.api.peers[i], "msg", [text], None)
						pid = self.api.query(qry)

		except KeyboardInterrupt:
			pass
	
	def close(self):
		self.api.close(self.usr_id)



# Global Vars
usr_id, pub_key = None, None
app = App()
app.api.set_listener(app.listener)

@eel.expose
def login(username, password):
	app.login(username, password)

@eel.expose
def signup(username, password):
	app.signup(username, password)

@eel.expose
def get_name():
	eel.reload(app.usr_id)

eel.init("web")
eel.start("login.html", mode = "default")

app.close()


