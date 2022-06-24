from pyxis_includes import *
from pyxis_utils    import *
from pyxis_types    import *


class Pyxis_API:
	def __init__(self):
		self.sv_addr = ("192.168.1.68", 5050)
	
		# Flags
		self.__listener_enabled = False
		self.running = True

		# List of cmds handled by api
		self.cmds = [PEERS_ADDR]

		# Process dictionary
		self.process = {}

		# Peers address
		self.peers = []

		# Socket stuff
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
		self.sock.bind(self.get_addr())
		
		self.__connect_to_server()
	
	def close(self):
		qry = pQuery(UNKNOWN, SERVER, DISCONNECT, [], None, None)
		pyxis_send(self.sock, self.sv_addr, qry)

		self.running = False
		exit()
	
	# Socket related functions
	def get_addr(self):
		ip = socket.gethostbyname(socket.gethostname())
		port = random.randint(5000, 5999) 
		return ip, port

	def __connect_to_server(self):
		qry = pQuery(UNKNOWN, SERVER, CONNECT, [], None, uuid.uuid4())
		pyxis_send(self.sock, self.sv_addr, qry)
	
	# Process handlers
	def create_new_process(self, pid, peers):
		if pid in self.process: return
		self.process.update({ 
			pid: {
				"completed": False, 
				"result"   : None, 
				"log"      : "",
				"values"   : [],
				"peers"    : peers
				} 
			})
	
	def __handle_process(self, value):
		pro_reg = self.process[value.pid]
		pro_reg["log"] = value.params[0]
		pro_reg["result"] = value.cmd

		value.params.pop(0)
		pro_reg["values"].append(value)
	
	def get_process_result(self, pid):
		pro_reg = self.process[pid]

		while not pro_reg["completed"]:
			if len(pro_reg["values"]) == pro_reg["peers"]: pro_reg["completed"] = True
			if pro_reg["result"] == FAILED: pro_reg["completed"] = True

		self.process.pop(pid)
		return pro_reg
	
	# Listener
	def __handle_cmds(self, qry):
		if qry.cmd == PEERS_ADDR:
			self.peers = qry.params

	def __listener(self, listener):
		while self.running:
			recv, addr = pyxis_recv(self.sock)

			if recv.pid in self.process:
				self.__handle_process(recv)

			elif recv.cmd in self.cmds:
				self.__handle_cmds(recv)

			else:
				listener(recv)

	def set_listener(self, listener):
		if not self.__listener_enabled: self.__listener_enabled = True
		threading.Thread(target = self.__listener, args = (listener, )).start()
	
	# Authenticate functions
	def login(self, username, pwd, app_id):
		if not self.__listener_enabled: 
			pyxis_error(f"Handle the listener before quering the data.")
			self.close()

		# Creating new process with the peer of `1`
		pid = uuid.uuid4()
		self.create_new_process(pid, 1)

		# Sending query to the server
		qry = pQuery(UNKNOWN, SERVER, LOGIN, [username, pwd], app_id, pid)
		pyxis_send(self.sock, self.sv_addr, qry)

		# Sending back the result
		result = self.get_process_result(pid)
		return result

	def signup(self, username, pwd, app_id):
		if not self.__listener_enabled: 
			pyxis_error(f"Handle the listener before quering the data.")
			self.close()

		# Creating new process with the peer of `1`
		pid = uuid.uuid4()
		self.create_new_process(pid, 1)

		# Sending query to the server
		qry = pQuery(UNKNOWN, SERVER, SIGNUP, [username, pwd], app_id, pid)
		pyxis_send(self.sock, self.sv_addr, qry)
		
		# Sending back the result
		result = self.get_process_result(pid)
		return result
	
	# Query Function
	def query(self, qry):
		pid1 = uuid.uuid4()
		pid2 = uuid.uuid4()

		self.create_new_process(pid1, 1) # Process for server
		self.create_new_process(pid2, len(self.peers) - 1) # Process between peers

		# Sending the server the qry to check the app id
		qry.pid = pid1
		pyxis_send(self.sock, self.sv_addr, qry)
		result = self.get_process_result(qry.pid)
		if result["result"] == FAILED: 
			pyxis_error(result["log"])
			self.close()

		# If app id is valid sending the query to the peers
		qry.pid = pid2
		for peer in self.peers:
			if peer != self.get_addr(): pyxis_send(self.sock, peer, qry)

		return pid2

