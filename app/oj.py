import requests
import json
from time import gmtime, strftime
from datetime import datetime
from config import Config
from buffer import Buffer
from threading import Lock

class OJ:

	Languages = {
		'C++' : '2',
		'C' : '1',
		'Java' : '3',
		'Python2' : '4',
		'Python3' : '5'
	}

	Verdicts = {}

	lock = Lock()

	@staticmethod
	def initial():

		with requests.session() as s:
			rsp = s.get("https://api.oj.nctu.me/verdicts/", cookies=Config.data["Agent"]["cookies"])
			res = json.loads(rsp.content)['msg']


			for data in res:
				OJ.Verdicts[data["id"]] = data['abbreviation']

			#print "Contest Time : {}~{}".format(OJ.ContestTime["start"], OJ.ContestTime["end"])
			#print "Contest Problems : "
			#for pid, val in OJ.problemArr:
				#print "{} : {}".format(pid, val["title"])
			
		return

	@staticmethod
	def getProblemsData(pid):
		with requests.session() as s:
			result = {}
			rsp = s.get('https://api.oj.nctu.me/problems/{0}/?problemId={0}'.format(pid), cookies=Config.data["Agent"]["cookies"])
			res = json.loads(rsp.content)['msg'] 
			result["title"] = res['title']

			rsp = s.get('https://api.oj.nctu.me/problems/{0}/executes/?problemId={0}'.format(pid), cookies=Config.data["Agent"]["cookies"])
			res = json.loads(rsp.content)['msg']

			result['exec_id'] = {}
			for exe in res:
				result['exec_id'][exe["language_id"]] = exe["id"]

		return result

	@staticmethod
	def submit(pid, lid, fname, file, prefix=""):
		pid = int(pid)
		lid = int(lid)
		code = prefix

                lines = file.readlines()
                lines[0] = lines[0].replace('\xef\xbb\xbf', '')
                lines[0] = lines[0].replace('\xef\xbf\xbe', '')
		for line in lines:
			code += line

		parm = {
			'problem_id':(None, pid),
			'execute_id':(None, Buffer.problems[pid]['exec_id'][lid]),
			'filename':(None, fname),
			'code':(None, code)
		}

		with requests.session() as s:
			rsp = s.post('https://api.oj.nctu.me/submissions/', data=parm, cookies=Config.data["Agent"]["cookies"])
			res = json.loads(rsp.content)
			
			if rsp.reason == "OK":
				return res["msg"]["id"]
			else:
				return None

	@staticmethod
	def updateResult(uids, subs):
		with OJ.lock:
			if (datetime.now()-Buffer.subDataUpTime).total_seconds() >= Config.data["Submissions"]["updateTime"]:
                                Buffer.subData = {uid : [] for uid in uids+[-1]}
				subs = {sub.sid : sub.uid for sub in subs}

				with requests.session() as s:
					for pid in Config.data["Problems"]:
						cmd = 'https://api.oj.nctu.me/submissions/?problem_id={}&user_id={}&group_id={}&count=1000000'.format(pid, Config.data["Agent"]["uid"], Config.data["Agent"]["group_id"])
						rsp = s.get(cmd, cookies=Config.data["Agent"]["cookies"])
						total = json.loads(rsp.content)["msg"]["submissions"]
						for sub in total:
							if sub["id"] not in subs.keys():
								continue

							tmp = dict()
							tmp["result"] = OJ.Verdicts[sub["verdict_id"]]
							tmp["pid"] = pid
							tmp["problem"] = Buffer.problems[pid]["title"]
							tmp["timeStr"] = sub["created_at"]
							tmp["time"] = datetime.strptime(sub["created_at"], "%Y-%m-%d %H:%M:%S")
							tmp["sid"] = sub["id"]
							tmp["uid"] = subs[tmp["sid"]]

							Buffer.subData[tmp["uid"] ] += [tmp]
							Buffer.subData[-1] += [tmp]

				for uid in Buffer.subData.keys():
					Buffer.subData[uid] = sorted(Buffer.subData[uid], key=lambda x : -x["sid"])


				Buffer.subDataUpTime = datetime.now()
		return

	@staticmethod
	def getCode(sid):
		with requests.session() as s:
			rsp = s.get('https://api.oj.nctu.me/submissions/{0}/file/'.format(sid), cookies=Config.data["Agent"]["cookies"])
			return rsp.content
		

if __name__ == "__main__":
	with open('data/config.json') as f:
		config = json.load(f)
	OJ.initialize(config)
	#oj = OJ()
	#oj.submit('522', '2', "main.cpp", "tmp/main.cpp")
	#print OJ.getCode(52958)
	print OJ.result(550, 57254)
	
