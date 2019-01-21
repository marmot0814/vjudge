from datetime import datetime
from config import Config

class Buffer:

	subData = {}
	scbData = {}
	scbDataFz = {}
	problems = {}

	subDataUpTime = datetime(1, 1, 1)
	scbDataUpTime = datetime(1, 1, 1)

	@staticmethod
	def initial(OJ):

		Buffer.subData = {}
		Buffer.problems = {pid : {} for pid in Config.data["Problems"]}

		for pid in Config.data["Problems"]:
			Buffer.problems[pid] = OJ.getProblemsData(pid)

		Buffer.scbData["pids"] = Buffer.scbDataFz["pids"] = Config.data["Problems"]
		Buffer.subDataUpTime = datetime(1, 1, 1)
		Buffer.scbDataUpTime = datetime(1, 1, 1)
