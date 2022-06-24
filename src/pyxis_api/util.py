from pyxis_api.conf        import *
from pyxis_api.pyxis_types import *
from pyxis_api.pyxis_const import *

# Terminal colors 
class Colors:
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLACK = '\033[30m'
    DEFAULT = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# Sucess, Error and warnings 
def pyxis_sucess(msg):
	print(f"{Colors.GREEN}[PYXIS SUCESS]: {msg}{Colors.DEFAULT}")

def pyxis_error(msg):
	print(f"{Colors.RED}[PYXIS ERROR]: {msg}{Colors.DEFAULT}")

def pyxis_warning(msg):
	print(f"{Colors.YELLOW}[PYXIS WARNING]: {msg}{Colors.DEFAULT}")

# Send and recv functions
def __pyxis_send(conn, data):
	time.sleep(DELAY)
	conn.send(data)

def __pyxis_recv(conn):
	time.sleep(DELAY)
	return conn.recv(BUFF_CAP)

def pyxis_send(conn, data):
	new_data = pickle.dumps(data)

	# If the data is below the buffer capacity
	if len(new_data) <= BUFF_CAP:
		info = pQuery(data.by, data.to, META, [f"{len(new_data)}:{0}"], None)
		__pyxis_send(conn, pickle.dumps(info))
		__pyxis_send(conn, new_data)
		return

	# If the data is bigger than the buffer
	padd = BUFF_CAP - (len(new_data) % BUFF_CAP)
	new_data += b" " * padd

	# Sending the packet information
	info = pQuery(data.by, data.to, META, [f"{len(new_data)}:{padd}"], None)
	__pyxis_send(conn, pickle.dumps(info))

	for i in range(0, len(new_data), BUFF_CAP):
		__pyxis_send(conn, new_data[i:i+BUFF_CAP])

def pyxis_recv(conn):
	info = pickle.loads(__pyxis_recv(conn))
	info = info.params[0].split(":")
	sz, padd = int(info[0]), int(info[1])
	
	# Collecting the data and combining it
	data = b""
	while len(data) < sz:
		data += __pyxis_recv(conn) 
	
	# Remove the excess padding
	data.strip(b" " * padd)
	return pickle.loads(data)

# Storage directory location
def pyxis_get_storage_path(ops):
	if ops == "Linux":
		if 'ANDROID_STORAGE' in os.environ:
			path = "/storage/emulated/0/Android/data/" 
			if not os.path.exists(path + PYXIS_STORAGE_DIR):
				os.mkdir(path + PYXIS_STORAGE_DIR)
			path += PYXIS_STORAGE_DIR + "/"
			return path
		else:
			path = os.path.expanduser("~") + "/.config/"
			if not os.path.exists(path + PYXIS_STORAGE_DIR):
				os.mkdir(path + PYXIS_STORAGE_DIR)
			path += PYXIS_STORAGE_DIR + "/"
			return path

	elif ops == "Windows":
		path = os.getenv('APPDATA')
		path = path.replace("\\" , '/')
		if not os.path.exists(path + PYXIS_STORAGE_DIR):
			os.mkdir(path + PYXIS_STORAGE_DIR)
		path += PYXIS_STORAGE_DIR + "/"
		return path
		

if __name__ == '__main__':
	print(pyxis_get_storage_path("Windows"))
