import sys
sys.path = ['.'] + sys.path

from app import db
from app.models import Submission

print Submission.query.all()
'''
with open('log/submissions', 'r') as file:
	for line in file.readlines():
		s = line.strip().split(',')
		sid = s[0].split(':')[1].strip()
		uid = s[1].split(':')[1].strip()
		pid = s[2].split(':')[1].strip()

		db.session.add(Submission(uid=uid, pid=int(pid), sid=int(sid)))
		db.session.commit()
'''
