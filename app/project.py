from flask import Flask, render_template, request, redirect,jsonify, url_for, flash
app = Flask(__name__)

import string
import random

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database import TestThing, Base


## OAuth
from flask import session as login_session 	# dict
import random, string 	# pseudorandom string for each session
from secrets import g_client_id, g_client_secret	# app secrets
# create flow obj from json client id, client secret and other OAuth2 params
# This json-formatted file stores client id, client secret and other Oauth params
# For G, these are params we got with created app in console.developers.google.com,
# and the JSON file is the client secret file dl under that app at that G acct
from oauth2client.client import flow_from_clientsecrets

# method for errors when trying to exchange one-time code for token
# the one-time code is the authorization, the token is the access token
from oauth2client.client import FlowExchangeError

# comprehensive http client library in Python
import httplib2

# also need JSON for this
import json

# turn return val from function into a real response obj to send off to client
from flask import make_response

# Apache 2 licensed http lib similar to urllib but with improvements
import requests

# make OAuth2Credentials object serializable
import base64

#Connect to Database and create database session
engine = create_engine('sqlite:///testdata.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


g_CLIENT_ID = json.loads(open('secrets_g.json', 'r').read())['web']['client_id']

# OAuth login
@app.route('/login')
def showLogin():
	state = "".join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
	login_session['state'] = state
	return render_template ('login.html', g_client_id=g_CLIENT_ID, STATE=login_session['state'])

# server-side route for getting G oauth2 token response
@app.route('/gconnect', methods=['POST'])
def gconnect():
	# verify that the user is the one making the request
	if request.args.get('state') != login_session['state']:
		response = make_response(json.dumps('Invalid state token'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	# collect the one-time code from our server
	code = request.data
	# upgrade the one-time code to a credentials object by exchanging it
	try:
		# will contain access token from our server
		oauth_flow = flow_from_clientsecrets('secrets_g.json', scope='')
		oauth_flow.redirect_uri = 'postmessage'
		credentials = oauth_flow.step2_exchange(code)   # initiate exchange
	# handle errors along the flow exchange
	except:
		response = make_response(json.dumps('Failed to upgrade authorization code.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	# if we got here, we have the credentials obj - check for valid access token
	access_token = credentials.access_token
	# let G verify if it's a valid token for use
	url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
	h = httplib2.Http()
	result = json.loads(h.request(url, 'GET')[1])

	# we do not have a working access token - send 500 error to client
	if result.get('error') is not None:
		response = make_response(json.dumps(result.get('error')), 500)
		response.headers['Content-Type'] = 'application/json'
		return response

	# we do not have the right access token (matching g id) - 401 error to client
	gplus_id = credentials.id_token['sub']
	if result['user_id'] != gplus_id:
		response = make_response(json.dumps("Token\'s user ID doesn\'t match given user ID."), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	# we do not have matching client ids - 401 error to client
	if result['issued_to'] != g_CLIENT_ID:
		response = make_response(json.dumps("Token\'s client ID does not match app\'s."), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	# check if user is already logged in
	stored_credentials = login_session.get ('credentials')
	stored_gplus_id = login_session.get ('gplus_id')
	if stored_credentials is not None and gplus_id == stored_gplus_id:
		# return success without resetting login vars again
		response = make_response(json.dumps("Current user is already connected."), 200)
		response.headers['Content-Type'] = 'application/json'

	# login was valid - store the access token for later
	login_session['credentials'] = credentials.access_token
	login_session['gplus_id'] = gplus_id

	# get more info about the user
	userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
	params = {'access_token': credentials.access_token, 'alt': 'json'}
	# request the info allowed by my token's scope
	answer = requests.get(userinfo_url, params = params)
	data = json.loads(answer.text)  	# store the info

	# store the specific data our app is interested in
	login_session['username'] = data['name']
	login_session['picture'] = data['picture']
	login_session['email'] = data['email']

	# Encode the payload using Base64.  This line is from here:
	# https://docs.python.org/3/library/email-examples.html
	print(login_session['username'])
	print(login_session['picture'])
	print(login_session['email'])

	# simple response that shows we were able to use user info
	o = '<h1>Welcome, %s!</h1>' % login_session['username']
	o += '<img src = "%s"' % login_session['picture']
	o += ' style = "width: 200px; height: 200px; border-radius: 50px; -webkit-border-radius: 50px; -moz-border-radius: 50px;">'
	flash('You are now logged in as %s' % login_session['username'])
	return o

@app.route('/')
def showMain():
	return render_template('content.html', content="Happy to be running here!")

@app.route('/things/<thing_id>')
def showThing(thing_id):
	try:
		data = session.query(TestThing).filter_by(id=thing_id).one()
		name = data.name
	except:
		name = 'nobody'
	return render_template('content.html', content="Happy to be showing you %s!" % name)

@app.route('/things')
def showThings():
	data = session.query(TestThing).all()
	return render_template("content.html", content="List of names in database:", data=data)

@app.route('/populate-database')
def populateDatabase():
	for n in range(10):
		random_name = "".join([random.choice(string.ascii_letters) for i in range(8)])
		session.add(TestThing(name=random_name))
	session.commit()
	return render_template('content.html', content="Built a list of names for you")

if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 8080)
