
class pQuery:
	def __init__(self, cmd, auth):
		self.cmd = cmd
		self.auth = auth 

class pResult:
	def __init__(self, log, data, sucess):
		self.log = log
		self.data = data
		self.sucess = sucess
