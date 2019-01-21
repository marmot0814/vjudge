#!/bin/bash
packages=("flask" "flask-wtf" "flask-sqlalchemy" "flask-migrate" "flask-login" "requests")
for pkg in ${packages[*]}
do
	pip2 install $pkg
done
