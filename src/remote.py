from pyxis_api.pyxis_api import *
from pyxis_api.util      import *

class Remote:
	def __init__(self):
		self.api = Pyxis_API()

	def run(self):
		query = pQuery(["CONNECT", "REMOTE"], None)
		res = self.api.query(query)
		if not res.sucess:
			pyxis_error(res.log)
		else:
			pyxis_sucess(res.log)

if __name__ == "__main__":
	remote = Remote()
	remote.run()
