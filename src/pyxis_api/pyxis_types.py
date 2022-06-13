
class pQuery:
	def __init__(self, by, to, cmd, params, auth):
		self.by = by
		self.to = to
		self.cmd = cmd
		self.params = params
		self.auth = auth 
	
	def __str__(self):
		return f"pQuery (\n  by: {self.by}\n  to: {self.to}\n  cmd: {self.cmd}\n  params: {self.params}\n  auth: {self.auth}\n)"

class pResult:
	def __init__(self, log, data, sucess):
		self.log = log
		self.data = data
		self.sucess = sucess
