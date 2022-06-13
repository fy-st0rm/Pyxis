# pyxis api
from pyxis_api.pyxis_types import *
from pyxis_api.pyxis_const import *
from pyxis_api.pyxis_api   import *

class Remote:
	def __init__(self):
		self.api = Pyxis_API()
	
	# Connect and Disconnect functions with pyxis server
	def __connect(self):
		qry = pQuery(REMOTE, PYX_SERVER, CONNECT, [REMOTE], None)
		res = self.api.query(qry)
		if res.cmd == SUCESS:
			pyxis_sucess(res.params[0])
		else:
			pyxis_error(res.params[0])
			exit(1)

	def __disconnect(self):
		qry = pQuery(REMOTE, PYX_SERVER, DISCONNECT, None, None)
		res = self.api.query(qry)
		if res.cmd == SUCESS:
			pyxis_sucess(res.params[0])
		else:
			pyxis_error(res.params[0])
			exit(1)


	# Registration function
	def __load_stored_data(self):
		data = []
		path = pyxis_get_storage_path(platform.system())
		files = os.listdir(path)

		for i in files:
			f_info = i.split(":")
			id     = f_info[0]
			chunk  = f_info[1]
			padd   = f_info[2]
			total  = f_info[3]
			file   = f_info[4]
			data.append((id, chunk, padd, total, file))

		return data
	
	def __register_data(self):
		data = self.__load_stored_data()
		qry  = pQuery(REMOTE, REM_HANDLER, REG_DATA, data, None) 
		res = self.api.query(qry)
		if res.cmd == SUCESS:
			pyxis_sucess(res.params[0])
		else:
			pyxis_error(res.params[0])
			exit(1)
	
	def run(self):
		self.__connect()
		self.__register_data()
		self.__disconnect()

if __name__ == "__main__":
	remote = Remote()
	remote.run()
	
