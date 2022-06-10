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
