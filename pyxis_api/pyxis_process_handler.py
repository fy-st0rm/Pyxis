from pyxis_includes import *
from pyxis_utils    import *
from pyxis_types    import *


class ProcessHandler:
	def __init__(self):
		self.process = {}

	def create_new_process(self, pid, peers):
		if pid in self.process: return
		self.process.update({ 
				pid: pResult(False, None, "", [], peers)
			})
	
	def handle_process(self, value):
		pro_reg = self.process[value.pid]
		pro_reg.log = value.params[0]
		pro_reg.result = value.cmd

		value.params.pop(0)
		pro_reg.values.append(value)
	
	def get_process_result(self, pid):
		pro_reg = self.process[pid]

		while not pro_reg.completed:
			if len(pro_reg.values) == pro_reg.peers: pro_reg.completed = True
			if pro_reg.result == FAILED: pro_reg.completed = True

		self.process.pop(pid)
		return pro_reg

