
# Constants
DELAY = 0.1
FORMAT = "utf-8"
BUFF_CAP = 65_500

PYXIS_STORAGE_DIR = ".pyxis_data"

# Pyxis Keywords:

# CMDS:
PEERS_ADDR = "<peers_addr>"
CONNECT = "<connect>"
DISCONNECT = "<disconnect>"

LOGIN = "<login>"
SIGNUP = "<signup>"

STORE = "<store>"
FETCH = "<fetch>"

# TAGS:
UNKNOWN = "<unknown>"
SERVER = "<server>"

# RESULT IDENTIFIER:
SUCESS = "<sucess>"
FAILED = "<failed>"
SKIP   = "<skip>"


# PYXIS TYPES:

class pQuery:
	def __init__(self, by, to, cmd, params, pid):
		self.by     = by
		self.to     = to
		self.cmd    = cmd
		self.params = params
		self.pid    = pid
	
	def __str__(self):
		return f"pQuery (\n  by: {self.by}\n  to: {self.to}\n  cmd: {self.cmd}\n  params: {self.params}\n  pid: {self.pid}\n)"


class pPackage:
	def __init__(self, uid, fname, padd, offset, total, data):
		self.uid = str(uid)
		self.fname = fname
		self.padd = int(padd)
		self.offset = int(offset)
		self.total = int(total)
		self.data = data
	
	def __str__(self):
		return f"pPackage: (\n  uid: {self.uid}\n  fname: {self.fname}\n  padd: {self.padd}\n  offset: {self.offset}\n  total: {self.total}\n  data: {self.data}\n)"


class pResult:
	def __init__(self, completed, result, log, values, peers):
		self.completed = completed
		self.result = result
		self.log = log
		self.values = values
		self.peers = peers

	def __str__(self):
		return f"pResult: (\n  completed: {self.completed}\n  result: {self.result}\n  log: {self.log}\n  values: {self.values}\n  peers: {self.peers}\n)"

