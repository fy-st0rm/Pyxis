import sys
import os
sys.path.append(os.path.abspath("../pyxis_api"))
from pyxis_api import *

class App:
	def __init__(self):
		self.api = Pyxis_API()
		self.usr_id = None
		self.pub_key = None
	
	def __connect(self):
		qry = pQuery(self.api.addr, self.api.sv_addr, CONNECT, [self.usr_id], None)
		pid = self.api.query(qry)
		res = self.api.process_handler.get_process_result(pid)
		if res.result == SUCESS:
			pyxis_sucess(res.log)
		else:
			pyxis_error(res.log)
		
	def __login(self):
		username = input("Username: ")
		pwd = input("Password: ")
		result = self.api.login(username, pwd)

		if result.result == SUCESS:
			pyxis_sucess(result.log)
			self.usr_id, self.pub_key = result.values[0].params
		else:
			pyxis_error(result.log)
			self.close()

	def __signup(self):
		username = input("Username: ")
		pwd = input("Password: ")
		result = self.api.signup(username, pwd)

		if result.result == SUCESS:
			pyxis_sucess(result.log)
			self.usr_id, self.pub_key = result.values[0].params
		else:
			pyxis_error(result.log)
			self.close()
			self.close()

	def __store(self):
		file = input("File> ")
		with open(os.path.join(file), "rb") as r:
			data = r.read()

		pyxis_warning("Storing file")
		res = self.api.store(file.split("/")[-1], data, self.pub_key)
		if res.result:
			pyxis_sucess(res.log)
			self.fid, self.total_chunks = res.values[0].params
			pyxis_sucess(f"File id: {self.fid} seperated into: {self.total_chunks} chunks")
		else:
			pyxis_error(res.log)

	def __fetch(self):
		pyxis_warning("Fetching file")
		res = self.api.fetch(self.fid, self.total_chunks, self.pub_key)
		if res.result == SUCESS:
			fname, data = res.values
			with open(fname, "wb") as w:
				w.write(data)
			pyxis_sucess(res.log)
		else:
			pyxis_error(res.log)
	
	def listener(self, qry, addr):
		if qry.cmd == "msg":
			print("\rpeer>", qry.params[0])

	def run(self):
		try:
			self.api.set_listener(self.listener)

			# self.__signup()
			self.__login()
			self.__connect()

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

if __name__ == "__main__":
	app = App()
	app.run()
	app.close()

    
