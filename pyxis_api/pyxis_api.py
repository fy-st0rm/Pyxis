from pyxis_includes import *
from pyxis_utils    import *
from pyxis_types    import *
from pyxis_process_handler import *
from pyxis_database import *


class Pyxis_API:
	def __init__(self):
		self.sv_addr = ("192.168.1.68", 6969)
	
		# Flags
		self.running = True

		# List of cmds handled by api
		self.cmds = [PEERS_ADDR, STORE, FETCH]

		# Process handler 
		self.process_handler = ProcessHandler()

		# Database handler
		self.pyxis_database = PyxisDatabase()

		# Peers address
		self.peers = {}

		# Socket stuff
		self.addr = self.generate_addr()
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind(self.addr)
		
		self.__connect_to_server()
	
	def get_peer_addr(self, peer_uid):
		if peer_uid in self.peers: return self.peers[peer_uid]
		return f"Peer with uid: {peer_uid} doesnt exists."
	
	def close(self, usr_id):
		qry = pQuery(self.addr, self.sv_addr, DISCONNECT, [usr_id], None)
		pyxis_send(self.sock, qry)

		self.running = False
		self.sock.close()
		exit()
	
	# Socket related functions
	def generate_addr(self):
		ip = socket.gethostbyname(socket.gethostname())
		port = random.randint(5000, 5999) 
		return ip, port

	def __connect_to_server(self):
		qry = pQuery(self.addr, self.sv_addr, b"0", [], uuid.uuid4())
		pyxis_send(self.sock, qry)

	# Listener
	def __handle_cmds(self, qry, addr):
		if qry.cmd == PEERS_ADDR:
			self.peers = qry.params

		elif qry.cmd == STORE:
			res = self.__store_package(qry.params[0], qry.params[1])
			res.by = qry.to; res.to = qry.by; res.pid = qry.pid
			pyxis_send(self.sock, res)

		elif qry.cmd == FETCH:
			res = self.__fetch_package(qry.params[0], qry.params[1])
			res.by = qry.to; res.to = qry.by; res.pid = qry.pid
			pyxis_send(self.sock, res)

	def __listener(self, listener):
		while self.running:
			recv, addr = pyxis_recv(self.sock)

			if   recv.pid in self.process_handler.process: self.process_handler.handle_process(recv)
			elif recv.cmd in self.cmds:					   self.__handle_cmds(recv, addr)
			else:					       				   listener(recv, addr)

	def set_listener(self, listener):
		threading.Thread(target = self.__listener, args = (listener, )).start()
	
	# Authenticate functions
	def login(self, username, pwd):
		# Creating new process with the peer of `1`
		pid = uuid.uuid4()
		self.process_handler.create_new_process(pid, 1)

		# Sending query to the server
		qry = pQuery(self.addr, self.sv_addr, LOGIN, [username, pwd], pid)
		pyxis_send(self.sock, qry)

		# Sending back the result
		result = self.process_handler.get_process_result(pid)
		return result

	def signup(self, username, pwd):
		# Creating new process with the peer of `1`
		pid = uuid.uuid4()
		self.process_handler.create_new_process(pid, 1)

		# Sending query to the server
		qry = pQuery(self.addr, self.sv_addr, SIGNUP, [username, pwd], pid)
		pyxis_send(self.sock, qry)
		
		# Sending back the result
		result = self.process_handler.get_process_result(pid)
		return result
	
	# Query Function
	def query(self, qry):
		pid = uuid.uuid4()
		qry.pid = pid

		self.process_handler.create_new_process(pid, 1)
		pyxis_send(self.sock, qry)
		return pid
	
	# Database queries
	def __load_zip(self, path, file, pub_key):
		with pyzipper.AESZipFile(path + file) as zf:
			zf.setpassword(pub_key.encode())
			data = zf.read(file.strip(".zip"))
		return data

	def __store_package(self, package, key):
		pyxis_sucess("Storing file.")
		path = pyxis_get_storage_path(platform.system())

		file_name = f"{package.uid}:{package.fname}:{package.padd}:{package.offset}:{package.total}"
		with pyzipper.AESZipFile(path + file_name + ".zip", "w", compression=pyzipper.ZIP_LZMA, encryption=pyzipper.WZ_AES) as zf:
			zf.setpassword(key.encode())
			zf.writestr(file_name, package.data)
		pyxis_sucess("Sucessfully stored file.")
		return pQuery(None, None, SUCESS, [f"Sucessfully stored data.", package.uid, package.total], None)
	
	def __fetch_package(self, file_id, pub_key):
		path = pyxis_get_storage_path(platform.system())
		files = os.listdir(path)
		
		pyxis_sucess(f"Fetching file.")
		packages = []
		for file in files:
			f_info = file.split(":")
			fid    = f_info[0]
			fname  = f_info[1]
			padd   = f_info[2]
			offset = f_info[3]
			total  = f_info[4].strip(".zip")

			if file_id == fid:
				try:
					data = self.__load_zip(path, file, pub_key)
					packages.append(pPackage(fid, fname, padd, offset, total, data))
				except Exception as e:
					return pQuery(None, None, FAILED, [f"Failed to fetch file because {e}"], None)
		
		if packages:
			pyxis_sucess(f"Sucessfully fetched")
			return pQuery(None, None, SUCESS, [f"Sucessfully fetched file `{file_id}`.", packages], None)
		else:
			pyxis_warning(f"File not here! SKIP")
			return pQuery(None, None, SKIP, [f"Couldnt found file: {file_id}"], None)
	
	def store(self, fname, data, pub_key):
		packages = self.pyxis_database.make_packages(fname, data)

		pyxis_sucess("Sending packages")
		address = list(self.peers.values())
		address.remove(self.addr)
		peer = 0

		pyxis_sucess(f"Storing into {len(packages)} chunks")

		i = 0
		res = None
		for package in packages:
			pid = uuid.uuid4()
			self.process_handler.create_new_process(pid, 1)
			
			qry = pQuery(self.addr, address[peer], STORE, [package, pub_key], pid)
			pyxis_send(self.sock, qry)

			res = self.process_handler.get_process_result(pid)
			if res.result == FAILED:
				break

			peer += 1
			if peer >= len(address): peer = 0

		result = res
		return result

	def fetch(self, file_id, total_chunks, pub_key):
		chunks = {}
		complete = False

		address = list(self.peers.values())
		address.remove(self.addr)
		peer = 0
		
		for i in range(total_chunks):
			pid = uuid.uuid4()
			self.process_handler.create_new_process(pid, 1)

			qry = pQuery(self.addr, address[peer], FETCH, [file_id, pub_key], pid)
			if address[peer] != self.addr: pyxis_send(self.sock, qry)
			peer += 1
			if peer >= len(address): peer = 0

			res = self.process_handler.get_process_result(pid)
			if res.result == FAILED:
				return res
			elif res.result == SKIP:
				continue
			
			# Values contains reply queries with fectched packages
			packages = res.values[0].params[0]
			fname = packages[0].fname
			padd  = packages[0].padd

			for package in packages:
				if package.offset not in chunks: chunks.update({package.offset: package.data})
				if len(chunks) >= total_chunks: 
					complete = True
					break

			if complete: break

		# Combining the chunks
		data = b""
		for i in range(total_chunks):
			data += chunks[i]
		data.strip(b" " * padd)

		# Creating new result
		result = pResult(True, SUCESS, res.log, [fname, data], total_chunks)
		return result
