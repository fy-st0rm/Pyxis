from pyxis_includes import *
from pyxis_utils    import *
from pyxis_types    import *


class PyxisDatabase:
	def make_packages(self, fname, data):
		file_id = uuid.uuid4()

		padd = BUFF_CAP - (len(data) % BUFF_CAP)			
		data += b" " * padd
		offset = 0
		total = len(data) / BUFF_CAP

		packages = []
		for i in range(0, len(data), BUFF_CAP):
			package = pPackage(file_id, fname, padd, offset, total, data[i:i+BUFF_CAP])
			packages.append(package)
			offset += 1

		return packages
