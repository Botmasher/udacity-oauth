# Adding Facebook and Other Providers

## 1. Introduction

- add more oauth options to app
- logins for users who have FB accounts
- this increases number of users who can use app
- walkthrough for adding Facebook OAuth login
- then discuss using other providers

## 2. Registering your App with Facebook

- Facebook as an additional OAuth provider (so far from lesson 2 used G+)
- first register your app on FB to create client ID and secret at https://developers.facebook.com
	- add product
	- setup "Facebook Login"
	- click the new option on left "Facebook Login"
	- add `http://localhost:5000` to "Valid OAuth redirect URIs"
	- make sure Client OAuth Login and Web OAuth Login are enabled in "Client OAuth Settings"
- manually create a `fbclientsecrets.json` to store client ID and secret
```
{
	"web": {
		"app_id": "",
		"app_secret": ""
	}
}
```

# 3. Client-Side Login with Facebook SDK
- two options for doing OAuth using Facebook
	1. import their JS SDK and use Facebook functions
	2. build your own auth
- our app uses JS on the client side (the `login.html` page)
- so we'll implement a login button with the SDK
	1. button to send request from client
	2. then get back "the short-lived access token"
	3. like G+ call, create AJAX call to send token to server
	4. on server side, trade token for a "long-lived" Python token

# 4. Quiz: Updating login.html

1. load the SDK, enabling cookies and any social plugins on the page
```JavaScript
window.fbAsyncInit = function() {
	FB.init({
		appId: '',
		cookie: true,
		xfbml: true,
		version: 'v2.2'
	});
};
```

2. call the SDK async so rest of login page can load without it
```JavaScript
(function(d, s, id) {
	var js, fjs = d.getElementsByTagName(s)[0];
	if (d.getElementsById(id)) return;
	js = d.createElement(s);
	js.id = id;
	js.src = "//connect.facebook.net/en_US/sdk.js";
	fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));
```

3. create the actual login button, specifying scope of authorization (here `"public_profile,email"`)
```HTML
	<fb:login-button scope="public_profile,email" onlogin="sendTokenToServer();">
		<a href='javascript:sendTokenToServer()'>Login with Facebook</a>
	</fb:login-button>
```

4. create the `sendTokenToServer()` method invoked above on button press
	- get token
	- send access token to server
	- whichever `url` you use in the request will need to be implemented in the app routes
```JavaScript
function sendTokenToServer() {
	// Get the access token
	var access_token = FB.getAuthResponse()['accessToken'];
	console.log(access_token);
	console.log('Welcome! Fetching your information.... ');

	// you can use the SDK to make API calls as well
	FB.api('/me', function(response) {
		console.log('Successful login for: ' + response.name);

		// Send access token to server via AJAX
		$.ajax({
			type: 'POST',
			url: '/fbconnect?state={{STATE}}',
			processData: false,
			data: access_token,
			contentType: 'application/octet-stream; charset=utf-8',
			success: function(result) {
				// Handle or verify the server response if necessary.
				if (result) {
					$('#result').html('Login Successful!</br>'+ result + '</br>Redirecting...');
			 		setTimeout(function() {
						window.location.href = "/restaurant";
			 		}, 4000);
				} else {
					$('#result').html('Failed to make a server-side call. Check your configuration and console.');
				}
			}
		});
	});
}
```

## 5. Update project.py (part I)
1. create an `fbconnect` function
2. get the short-lived token from the `request.data`
3. exchange access token for a long-lived token
	- send `app_id`
	- send `app_secret` to verify server's identity
	- token includes `expires` field for length of token validity (up to 2 months)
	- strip the expiration tag by splitting string: `result.split("&")[0]`
4. make API calls using the new token
	- populate login session
```Python
	# url = #(profile info URL with your token)
	result = h.request(url, 'GET')[1]
	data = json.loads(result)
	login_session['username'] = data['name']
	login_session['email'] = data['email']
	login_session['facebook_id'] = data['id']
```
	- a separate API call is required for profile pic
```Python
	# url = #(profile pic URL with your token)
	result = h.request(url, 'GET')[1]
	data = json.loads(result)
	login_session['picture'] = data['data']['url']
```
	- _update_: as of API v2.2 email is not returned by default
	- _update_: the URL structure as of the latest class update has changed
```Python
	url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email' % token
```
5. use same code from G+ login to find user or to create user
	- send same "Welcome" splash screen, welcoming user with name and pic

## 6. Update project.py (part II)
- reject access token on user logout
1. create `fbdisconnect` function
2. if request succeeds, depopulate `login_session`
```Python
@app.route('/fbdisconnect')
def fbdisconnect():
	facebook_id = login_session['facebook_id']
	url = 'https://API_URL_HERE/&s/permissions' & facebook_id
	h = httplib2.Http()
	result = h.request(url, 'DELETE')[1]
	del login_session['username']
	del login_session['email']
	del login_session['picture']	
	del login_session['user_id']
	del login_session['facebook_id']
	return "logged user out"
```
3. think beyond this to work with disconnecting from other providers
	1. create new value in `login_session` to store the provider
	2. set `login_session['provider']` to `"google"` in `gconnect`
	3. set `login_session['provider']` to `"facebook"` in `fbconnect`
	4. create just a `disconnect()` function that branches to delete data based on the provider

## 7. Quiz: Updating project.py Code
- note that Facebook requires sending access token with the id to disconnect!
- update the template to include a link for logging in or disconnection
	- if `'username'` is not in the session, show login link
	- otherwise show disconnect link
- fire up server and test app
	- you should have option to connect using G or FB if try to log in
	- you should see simple disconnect link if logged in
	- you should be able to edit pages you own

## 8. Exploring other OAuth 2.0 Providers
- always start with the dev page of the provider you're interested in
- implementations vary as did between G and FB
- flow for obtaining, verifying, using tokens should remain
- consider these providers: Amazon, GitHub, Paypal

## 9. Outro
- that's the end of the course on implementing OAuth 2 in web apps!
- keep learning about OAuth and web app security
- play it safe!
- https://oauth.net/2/
