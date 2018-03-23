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

## 6. Update project.py (part II)
