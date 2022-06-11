import platform
import os

dev = platform.system()
if dev == "Linux":
	path = os.path.expanduser("~")
	print(path)


