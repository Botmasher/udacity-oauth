# Creating a Google Signin

## Types of Flow

- Flow 1: initiated by browser in JS, passing token to G+ that's passed back
	- client-side is quick and easy
	- but trusts browser/mobile and server cannot make API calls for user

- Flow 2: server side, server obtains the token on behalf of user (user can revoke)
	- server-side is more powerful
	- but server now responsible for implementing session tracking for users
	- secure storage and access tokens

- G+ hybridized flow: authent on client, but server makes API calls for client 
	- https://developers.google.com/identity/protocols/OAuth2#scenarios
	- even if hack access code btwn server & G, can't do stuff w/o "client secret"

## Get initial app running

- CLONED REPO gives me trouble.
	- I can clone, bring up vagrant, ssh in and navigate to the oauth directory
	- I can see all the listed py files there
	- I can run the db create and the db populate scripts just fine
	- I can run the project startup script just fine
	- when I navigate to the localhost port I see nothing
		- issue continues when I change project py and copy/paste e.g. localhost:8020
- USE my FoodBase project instead! It works just fine.
	- it's in a separate udacity-fullstack folder
	- navigate to vagrant/, vagrant up, vagrant ssh, then to /vagrant/finalProject
	- now let's implement oauth on this thing!

## Steps

1. setup to communicate with API library at console.developers.google.com
	- create new project
	- API > credentials
	- create new client id
	- now have "Client ID", "Client secret" and "Creation date"
2. Configure local version of code to work
	- Edit Client Settings
	- find Authorized JS Origins
	- add localhost:port (where port is the 4 ints you're using)
	- if you're also using the IP version (0.0....), this needs added as well
3. Use client ID and secret to add OAuth to app
	- Anti-Forgery State Tokens
	- make sure that the user is actually the one doing a request
	- unique session token that client side returns alongside authorization token
	- in later steps, verify this unique session token w server on all reqs
4. imports for Login Session in Flask app
	- Python imports at top of Flask view
```
from flask import session as login_session 	# this is a dict
import random, string 	# to create pseudorandom string for each session
```

5. create showLogin that makes the state var (32 chars, mix uppercase + digits)
- store that state as login_session['state'] to use later
```
@app.route('/login')
def showLogin():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
	login_session['state'] = state
	return "Current session state: %s" % login_session['state']
```
- for x-site request forgery, attacker would have to guess this code to make a request on user's behalf
- later, we'll check to make sure user and login session have same state val

6. Make an actual button user can click to login
- create new login template in project templates folder
- inside the new template's `<head>` tags, include the following scripts:
```
<script src = "//ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js">
</script>
<script src = "https://apis.google.com/js/client:platform.js?onload=start" async defer></script>
```
- in the body, create a div to hold the actual G signin data:
```
		<div id = "signinButton">
			<span class = "g-signin"
				data-scope = "openid"
				data-clientid = "YOUR CLIENT ID HERE"
				data-redirecturi = "postmessage"
				data-accesstype = "offline"
				data-cookiepolicy = "single_host_origin"
				data-callback = "signinCallback"
				data-approvalprompt = "force">
			</span>
		</div>
		<div id = "result"></div>
```
- `data-scope` : which G resources we want to be able to access. Compare the documentation to see kind of info you'll get in res obj (e.g. name, email, ...)
	- should read `"openid email"` to retrieve a user's email
- `data-clientid` : the client id value generated when creating project at console.developers.google.com
- `data-redirecturi` : sends a post messg, enabling one-time use codeflow
- `data-accesstype` : do you want to send api calls even if user not logged in?
- `data-cookiepolicy` : scope of uri that can access cookie. Single origin if just one host name and no subdomains.
- `data-callback` : the cb to pass onetime use code and access token if user grants access to profile data
- `data-approvalprompt` : user must login each time visit the login page (no check for already logged in). *Debug friendly, but disable in production!*

7. Change views.py login to render the login template
```
	return render_template ('login.html') 	 # but .php in my example
```

8. Bring Vagrant up, run the server and test the `/login` endpoint!
- Nothing interesting happens upon logging in... yet.

9. Callback method to handle response sent to client
- remember flow: user authenticates -> G sends response to CB
	- response includes access token
	- response includes one-time code
	- the one-time code is for our app (server)
	- the access token is for making calls from the browser
- add script just before closing body tags in login template
	- whatever you named the cb in the signin obj data-callback above
```
		<script>
		function signinCallback (authRes) {
			if (authRes['code']) { 	// if param called 'code', G auth was successful
				// Hide the G signin button
				$('#signinButton').attr('style', 'display: none');
				// ajax call passing the one-time code onto the server
				$.ajax({
					type: 'POST',
					// WE will define this gconnect method on our server next
					// send state var to use our check against x-site ref forgery
					url: '/gconnect?state={{STATE}}',
					// tell jQuery not to process the result into str
					processData: false,
					// octet-stream is arbitrary binary stream of data
					contentType: 'application/octet-stream; charset=utf-8',
					data: authRes['code'],
					// 200 code response - log the user into app
					success: function(res) {
						if (res) {
							$('#result').html('Login successful!<br>'+res+'<br>Redirecting...');
							setTimeout (function() {
								window.location.href = '/';
							}, 3000);
						}
					}
				});
			}
		}
		</script>
```
- make sure you have an empty div with id "result" to use the above success cb

10. Now back to views logic: several imports needed
```
# create flow obj from json client id, client secret and other OAuth2 params
# This json-formatted file stores client id, client secret and other Oauth params
# For G, these are params we got w created app in console.developers.google.com,
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
```

11. Navigate to G dev console again. Select project credentials. Download JSON.
- rename downloaded file to `client_secrets.json`
- store it in the same directory as `project.py` (the server I guess?)

12. Reference the client secrets file in views logic (directly below those imports)
```
CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
```

13. Define the gconnect method/route for that login template ajax call above
```
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
		oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
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
		response = make_response(json.dumps('Token\'s user ID doesn\'t match given user ID.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	# we do not have matching client id's - 401 error to client
	if result['issued_to'] != CLIENT_ID:
		response = make_response(json.dumps('Token\'s client ID does not match app\'s.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	# check if user is already logged in
	stored_credentials = login_session.get ('credentials')
	stored_gplus_id = login_session.get ('gplus_id')
	if stored_credentials is not None and gplus_id == stored_gplus_id:
		# return success without resetting login vars again
		response = make_response(json.dumps('Current user is already connected.'), 200)
		response.headers['Content-Type'] = 'application/json'

	# login was valid - store the access token for later
	login_session['credentials'] = credentials
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

	# simple response that shows we were able to use user info
	o = '<h1>Welcome, %s!</h1>' % login_session['username']
	o += '<img src = "%s"' % login_session['picture']
	o += ' style = "width: 200px; height: 200px; border-radius: 50px; -webkit-border-radius: 50px; -moz-border-radius: 50px;">'
	flash('You are now logged in as %s' % login_session['username'])
	return o
```

14. Check errors and scopes. I'm having trouble with code above, so some of the things I had to change to avoid 401 errors and 500 errors:
- stored credentials.access_token instead of credentials
```
login_session['credentials'] = credentials.access_token
```
- stopped storing email at least with these scopes (is this because of account settings or because of the scope?)
```
# login_session['email'] = data['email']
```

15. Add disconnect code to revoke token and reset login_session. TEST this URI.
```
@app.route('/gdisconnect')
def gdisconnect():
	credentials = login_session.get('credentials')
	# we don't have record of a user that we can disconnect
	if credentials is None:
		response = make_response(json.dumps('Current user isn\'t connected.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	# pass access token to G url for revoking tokens
	access_token = credentials.access_token
	url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
	# hit url and store response in a results object
	h = httplib2.Http()
	result = h.request(url, 'GET')[0]

	# successful response
	if result['status'] == '200':
		# reset our app login_session data
		del login_session['credentials']
		del login_session['gplus_id']
		del login_session['username']
		#del login_session['email']
		del login_session['picture']
		# pass client successful disconnect
		response = make_response(json.dumps('User successfully disconnected.'), 200)
		response.headers['Content-Type'] = 'application/json'
		return response
	# invalid token or somehow logout not successful
	else:
		response = make_response(json.dumps('Failed to revoke token and disconnect user.'), 400)
		response.header['Content-Type'] = 'application/json'
		return response
```

16. Protect your pages from non-logged-in users
- under a method like `/restaurant/create`
```
if 'username' not in login_session:
	return redirect('/login')
```
- pay attention to user experience
	- annoying to fill out a form, submit it, only to hit login wall
- often read makes sense unrestricted, then c/u/d restricted
- what about users modifying other user data? Permission system.
