
# Constants
DELAY = 0.1
FORMAT = "utf-8"
BUFF_CAP = 4098

# Pyxis Keywords:

# CMDS:
PEERS_ADDR = "<peers_addr>"
CONNECT = "<connect>"
DISCONNECT = "<disconnect>"
LOGIN = "<login>"
SIGNUP = "<signup>"

# TAGS:
UNKNOWN = "<unknown>"
SERVER = "<server>"

# RESULT IDENTIFIER:
SUCESS = "<sucess>"
FAILED = "<failed>"


class pQuery:
	def __init__(self, by, to, cmd, params, app_id, pid):
		self.by     = by
		self.to     = to
		self.cmd    = cmd
		self.params = params
		self.app_id = app_id
		self.pid    = pid
	
	def __str__(self):
		return f"pQuery (\n  by: {self.by}\n  to: {self.to}\n  cmd: {self.cmd}\n  params: {self.params}\n  auth: {self.app_id}\n  pid: {self.pid}\n)"

