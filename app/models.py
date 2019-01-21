from flask_login import UserMixin
from app import login, db
from oj import OJ

class User(UserMixin, db.Model):

	uid = db.Column(db.String(7), primary_key=True)
	pwd = db.Column(db.String(10))
	adm = db.Column(db.Boolean, default=False)

	def get_id(self):
		return self.uid
	
	@staticmethod
	def add(user):
		db.session.add(user)
		db.session.commit()

@login.user_loader
def load_user(uid):
	return User.query.get(uid)


class Submission(db.Model):

	sid = db.Column(db.Integer, primary_key=True)
	pid = db.Column(db.Integer)
	uid = db.Column(db.String(7), db.ForeignKey('user.uid'), index=True)

	@staticmethod
	def add(sub):
		db.session.add(sub)
		db.session.commit()

class Bulletin(db.Model):

	bid = db.Column(db.Integer, primary_key=True)
	uid = db.Column(db.String(7), db.ForeignKey('user.uid'), index=True)
	data = db.Column(db.String(256))
	typ = db.Column(db.String(32))


	def serialize(self):
		return	{
			'bid': self.bid,
			'uid': self.uid, 
			'data': self.data,
			'typ': self.typ,
		}
