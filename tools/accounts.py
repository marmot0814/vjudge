import sys
sys.path = ['.'] + sys.path


from app import db
from app.models import User

User.query.delete()
with open("data/accounts") as file:
	for line in file:
		uid,pwd,adm = line.strip().split('\t')
		db.session.add(User(uid=uid, pwd=pwd,adm=(adm=="True")))
	db.session.commit()

for user in User.query.all():
	print "uid {}\tpwd {}\t adm {}".format(user.uid, user.pwd, user.adm)