import json
from datetime import datetime

def timeToDt(s):
	return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")

class Config:
	data = {}

	@staticmethod
	def load():
		with open("data/config.json") as f:
			Config.data = json.load(f)
			Config.data["Time"]["start"] = timeToDt(Config.data["Time"]["start"])
			Config.data["Time"]["end"] = timeToDt(Config.data["Time"]["end"])
			Config.data["Time"]["startStr"] = Config.data["Time"]["start"].isoformat()
			Config.data["Time"]["endStr"] = Config.data["Time"]["end"].isoformat()
			
			Config.data["FileDir"], Config.data["FileName"] = Config.data["File"].rsplit('/', 1)
			Config.data["Scoreboard"]["freeze"] = timeToDt(Config.data["Scoreboard"]["freeze"])
