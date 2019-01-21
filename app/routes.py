from flask import render_template, redirect, url_for, flash, request, jsonify, send_from_directory, make_response
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.utils import secure_filename
from sqlalchemy import asc, desc

from app import app, db
from app.models import User, Submission, Bulletin
from app.forms import LoginForm, SubmitForm

from oj import OJ
from buffer import Buffer
from config import Config
import os

from datetime import datetime
from math import floor
import json
from threading import Lock

def ok_addr(addr):
        return True
	#return addr.startswith("140.113.") or addr == '127.0.0.1'
	#return addr in ['140.113.209.196', '140.113.209.197', '140.113.209.198', '127.0.0.1']  


def create_response(msg):
	resp = make_response(msg)
	#resp.headers['Content-Security-Policy'] = "default-src 'self'"
	resp.headers['X-XSS-Protection'] = '1; mode=block'
	return resp


@app.route('/')
@app.route('/index')
@login_required
def index():

	if datetime.now() < Config.data["Time"]["start"]:
		return create_response(render_template('index_wait.html'))

	form = SubmitForm()

	return create_response(render_template('index.html', form=form))

@app.route('/submissions', methods=['GET'])
@login_required
def submission():
	OJ.updateResult([ usr.uid for usr in User.query.all() ], Submission.query.all())
	if current_user.adm:
		pageSz  = int(request.args.get('pageSz')) if 'pageSz' in request.args else 50
		pageNum = int(request.args.get('page')) if 'page' in request.args else 1
		allSubs = Buffer.subData[-1]
	else:
		pageSz  = 10
		pageNum = int(request.args.get('page')) if 'page' in request.args else 1
		allSubs = Buffer.subData[current_user.uid]
	
        beg = max(0, (pageNum-1)*pageSz)
	end = min(len(allSubs), beg+pageSz) if pageSz > 0 else len(allSubs)
	res = allSubs[beg:end]

	tot = (len(allSubs)+pageSz-1)/pageSz if pageSz > 0 else 0

	return jsonify(res=res[::-1], tot=tot)

@app.route('/getContestTime', methods=['GET'])
def getContestTime():

	return jsonify({"start" : Config.data["Time"]["startStr"], "end" : Config.data["Time"]["endStr"]})

@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('/'))

	form = LoginForm()

	if form.validate_on_submit():

		user = User.query.filter_by(uid=form.username.data, pwd=form.password.data).first()
		
		if user == None:
			flash('Invalid username or password')
			return redirect(url_for('login'))

		login_user(user)

		return redirect(url_for('index'))

	return create_response(render_template('login.html', form=form))


@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('login'))

def file_ext(fname):
	return fname.rsplit('.', 1)[1]

def ok_file(file):
	return file.content_length <= 10 and '.' in file.filename and file_ext(file.filename) in ['c', 'cpp', 'py', 'java']

@app.route('/submit', methods=['POST'])
@login_required
def submit():

	form = SubmitForm()
	SubmitTime = datetime.now()

	if not current_user.adm and not ok_addr(request.remote_addr):
		flash("Invalid submission")
		with open('log/badIP', 'a') as file:
			file.write("{}	{}	{}\n".format(current_user.uid, SubmitTime, request.remote_addr))
	elif SubmitTime <= Config.data["Time"]["end"] and SubmitTime >= Config.data["Time"]["start"]:
		f = form.code.data
		SubmitTime = SubmitTime.strftime("%Y-%m-%d %H:%M:%S")
		sid = None
		if ok_file(f):

                        prefix = "VJudge Submission, {{User:'{}', Time:'{}', Language:'{}'}}\n".format(current_user.uid, SubmitTime, form.language.data)
			if file_ext(f.filename) == 'py':
				prefix = "#" + prefix
			else:
				prefix = "//" + prefix

			if Config.data["User"]["maxSubmission"] != -1 and Config.data["User"]["maxSubmission"] <= len(Submission.query.filter_by(uid=current_user.uid).all()):
				flash("Too many submissions")
				return redirect(url_for('index'))
			else:
				sid = OJ.submit(form.problem.data, form.language.data, "Main.{}".format(file_ext(f.filename)), f, prefix=prefix)
		else:
			flash("Invalid file extension")
			return redirect(url_for('index'))

		if sid == None:
			flash("Submitted failed, please try again later")
		else:
			with open("log/submissions", "a") as log:
				log.write("sid: {}, user:{}, pid:{}, lang:{}, time:{}\n".format(sid, current_user.uid, form.problem.data, form.language.data, SubmitTime))
			
			db.session.add(Submission(sid=sid, uid=current_user.uid, pid=form.problem.data))
			db.session.commit()
		return redirect(url_for('index'))
	else:
		flash("Invalid submission")
	return redirect(url_for('index'))


@app.route('/code', methods=['GET'])
@login_required
def code():
	 sid = request.args.get('sid')
	 sub = Submission.query.filter_by(sid=sid).first()
	 if current_user.adm or (sub != None and sub.uid == current_user.uid):
	 	return "<plaintext>{}".format(OJ.getCode(sid))
	 else:
	 	flash("Permission denied")
	 	return redirect(url_for('index'))

@app.route('/ask', methods=['POST'])
@login_required
def ask():

	data = request.form['data'].strip()
	if len(data) == 0:
		flash("Empty question?")
	else:
		db.session.add(Bulletin(data=data, typ="asking", uid=current_user.uid))
		db.session.commit()

	return redirect(url_for('index'))


@app.route('/styles.css', methods=['GET'])
def getCSS():
	return create_response(render_template('styles.css'))

@app.route('/bulletins', methods=['GET'])
@login_required
def getBulletins():

	if current_user.adm:
		buls = Bulletin.query.all()
	else:
		buls = Bulletin.query.filter((Bulletin.typ != "asking") | (Bulletin.uid == current_user.uid)).all()

	buls = sorted(buls, key=lambda b: b.bid)
	buls = [bul.serialize() for bul in buls]
	
	return jsonify(buls=buls)

@app.route('/admin/bulletins', methods=['GET', 'POST'])
@login_required
def bulletins():
	if current_user.adm:
		if request.method == "POST":
			
			bid = int(request.form['bid']) if 'bid' in request.form.keys() else -1
			data = request.form['data']
			typ = request.form['type']
			bul = Bulletin.query.filter_by(bid=bid).first()
		
			if bul == None:
				db.session.add(Bulletin(data=data, typ=typ, uid=current_user.uid))
			elif 'Delete' in request.form.keys():
				db.session.delete(bul)
			else:
				bul.data = data
				bul.typ = typ
			db.session.commit()

		return create_response(render_template('bulletins.html'))
	else:
		flash("Permission denied")
		return redirect(url_for('index'))

@app.route('/admin/submissions', methods=['GET'])
@login_required
def adminSubmissions():
	if current_user.adm:
		return create_response(render_template('submissions.html'))
	else:
		flash("Permission denied")
		return redirect(url_for('index'))


@app.route('/admin/config', methods=['GET'])
@login_required
def loadConfig():
	if current_user.adm:
		Config.load()
		OJ.initial()
                Buffer.initial(OJ)
		return jsonify(contestTime=Config.data["Time"], problems=Buffer.problems);
	else:
		flash("Permission denied")
		return redirect(url_for('index'))

lock = Lock()

def updateScoreboard():
	with lock:
		if (datetime.now()-Buffer.scbDataUpTime).total_seconds() >= Config.data["Scoreboard"]["updateTime"]:
			updateScoreboardData(Buffer.scbDataFz, True)
			updateScoreboardData(Buffer.scbData, False)
			Buffer.scbDataUpTime = datetime.now()

def updateScoreboardData(data, fz):
				
	data["users"] = [ usr.uid for usr in User.query.all() if not usr.adm ]
	data["table"] = {uid : {pid : [None, 0] for pid in data["pids"]} for uid in data["users"]}
	data["solved"] = {uid : 0 for uid in data["users"]}
	data["penalty"] = {uid : 0 for uid in data["users"]}
	data["first"] = {pid : None for pid in Config.data["Problems"]}
	OJ.updateResult([usr.uid for usr in User.query.all()], Submission.query.all())
	res = Buffer.subData[-1]
	
	for i in range(len(res)-1, -1, -1):
		sub = res[i]
		if not sub["uid"] in data["table"] or data["table"][sub["uid"]][sub["pid"]][0] not in [None, -1]:
			continue

		if (fz and (sub["time"] >= Config.data["Scoreboard"]["freeze"])) or sub["result"] == "Pending": 
			data["table"][sub["uid"]][sub["pid"]][0] = -1
			data["table"][sub["uid"]][sub["pid"]][1] += 1
		elif sub["result"] == "AC":
			data["table"][sub["uid"]][sub["pid"]][0] = int(floor((sub["time"]-Config.data["Time"]["start"]).total_seconds()/60))
			data["solved"][sub["uid"]] += 1
			data["penalty"][sub["uid"]] += data["table"][sub["uid"]][sub["pid"]][1]*20 + data["table"][sub["uid"]][sub["pid"]][0]

			if data["first"][sub["pid"]] is None or sub["time"] < data["first"][sub["pid"]][0]:
				data["first"][sub["pid"]] = (sub["time"], sub["uid"])
		else:
			data["table"][sub["uid"]][sub["pid"]][1] += 1
	
	rank = [(data["solved"][uid], -data["penalty"][uid], uid) for uid in data["users"]]
	rank = sorted(rank)[::-1]
	data["rank"] = {uid : 1 for uid in data["users"]}
	for i in range(1, len(rank)):
		if rank[i][:2] == rank[i-1][:2]:
			data["rank"][rank[i][2]] = data["rank"][rank[i-1][2]]
		else:
			data["rank"][rank[i][2]] = i+1

	data["users"] = sorted(data["users"], key=lambda x : data["rank"][x])
			
			

@app.route('/scoreboard', methods=['GET'])
@login_required
def scoreboard():
	if Config.data["Scoreboard"]["public"]:
		updateScoreboard()
                if datetime.now() >= Config.data["Time"]["end"]:
		    return create_response(render_template('scoreboard.html', Data=jsonify(data=Buffer.scbData)))
                else:
        	    return create_response(render_template('scoreboard.html', Data=jsonify(data=Buffer.scbDataFz)))
	else:
		flash("Permission denied")
		return redirect(url_for('index'))

@app.route('/admin/scoreboard', methods=['GET'])
@login_required
def adminScoreboard():
	if current_user.adm:
		updateScoreboard()
		return create_response(render_template('scoreboard.html', Data=jsonify(data=Buffer.scbData)))
	else:
		flash("Permission denied")
		return redirect(url_for('index'))

@app.route('/problems', methods=['GET'])
@login_required
def downloadZip():

	return send_from_directory(directory=Config.data["FileDir"], filename=Config.data["FileName"])
