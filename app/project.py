from flask import Flask, render_template, request, redirect,jsonify, url_for, flash
app = Flask(__name__)

import string
import random

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database import TestThing, Base

# OAuth
from flask import session as login_session 				# dict
import random, string 														# pseudorandom string for each session
from secrets import g_client_id, g_client_secret	# app secrets

#Connect to Database and create database session
engine = create_engine("sqlite:///testdata.db")
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# OAuth login
@app.route("/login")
def showLogin():
	state = "".join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
	login_session['state'] = state
	return "Current session state: %s" % login_session['state']

@app.route('/')
def showMain():
	return render_template("content.html", content="Happy to be running here!")

@app.route("/things/<thing_id>")
def showThing(thing_id):
	try:
		data = session.query(TestThing).filter_by(id=thing_id).one()
		name = data.name
	except:
		name = "nobody"
	return render_template("content.html", content="Happy to be showing you %s!" % name)

@app.route("/things")
def showThings():
	data = session.query(TestThing).all()
	return render_template("content.html", content="List of names in database:", data=data)

@app.route("/populate-database")
def populateDatabase():
	for n in range(10):
		random_name = "".join([random.choice(string.ascii_letters) for i in range(8)])
		session.add(TestThing(name=random_name))
	session.commit()
	return render_template("content.html", content="Built a list of names for you")

if __name__ == "__main__":
	app.secret_key = "super_secret_key"
	app.debug = True
	app.run(host = '0.0.0.0', port = 8080)
