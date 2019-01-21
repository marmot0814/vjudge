from random import choice
import string

with open("data/users") as inp, open("data/accounts", "w") as out:


        pwdchr = list(string.ascii_letters+string.digits)
        pwdchr.remove('0')
        pwdchr.remove('O')
        pwdchr.remove('1')
        pwdchr.remove('l')


	for line in inp:
		sid = line.strip()
                pwd = ''.join(choice(pwdchr) for i in range(8))
		out.write("{}\t{}\t{}\n".format(sid, pwd, False))
