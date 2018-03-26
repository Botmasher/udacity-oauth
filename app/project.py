from flask import Flask, render_template, request, redirect,jsonify, url_for, flash
app = Flask(__name__)

import string
import random

import Markup

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database import TestThing, Base

#Connect to Database and create database session
engine = create_engine('sqlite:///testdata.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
def showMain():
	return render_template("content.html", content="Happy to be running here!")

@app.route('/things/<thing_id>')
def showThing(thing_id):
	data = session.query(TestThing).filter_by(id=thing_id).one()
	return render_template("content.html", content="Happy to be showing you %s!" % data.name)

@app.route('/things/')
def showThings():
	data = session.query(TestThing).all()
	return render_template("content.html", content="Happy to be showing you %s!" % data)

@app.route('/populate-database/')
def populateDatabase():
	output = ""
	for n in range(10):
		random_name = "".join([random.choice(string.ascii_letters) for i in range(8)])
		session.add(TestThing(name=random_name))
		output += "<li>%s</li>" % random_name
	session.commit()
	output = "<ul>%s</ul>" % output
	return render_template("content.html", content="<p>Built a list of names for you:</p>%s" % output)

if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 8080)
