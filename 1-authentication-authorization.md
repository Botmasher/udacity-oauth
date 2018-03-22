#Authentication vs Authorization

## Intro & Course Map

- using version of Flask restaurants app like one I built for Full Stack Foundations
- will be provided the above app if needed
- build on JS, Ajax, jQuery courses as well as Python and Flask
- will be restricting access to authenticated users
- need FB and G+ accounts to do the exercises
- won't be doing heavy math of cybersecurity & crypto
- won't cover making your own self-made auth sys (OAuth 2 server)

## Authentication

- Authentication: process of verifying you are who you say you are (any login!)
	- e.g. picture on passport. BUT not foolproof
	- e.g. authenticity of artifacts through carbon dating
	- e.g. visit Paypal and getg certificate saying browser verifies it's Paypal
	- e.g. password
- ALWAYS people trying to cheat the system when system tries to verify truth of sth
- A LOT goes into authentication system:
	- strong pwds
	- strong encryption (algorithm)
	- secure client/server communication
	- securing pwd storage in encrypted db
	- pwd recovery quickly and securely
	- 2-factor authentication (pwd plus a special key)
	- protect against man-in-the-middle attacks
- Implementing those features is hard. Some on client, some server. Sometimes both.
	- strong pwds only on client side (JS) allows users to mimick by faking http req
	- man in the middle protection also must be done on both endpoints
- Has someone solved these problems before? Yes! Ask a trusted third party.
	- auth checks their third-party security system and reports back to you
	- requires communication between all three parties
- User login to 3 party, get auth. I ask user permission. Then I access 3 party data.
	- BUT user doesn't want me to have EVERYTHING in their profile and data

## Authorization

- Authorization: process of verifying your right to resource you're trying to access
	- 3 party auth providers ask if you want to grant the website access to certain data
- also, think abt bash access controller. Even once logged in, cannot do everything
	- adduser
- usu Authorization after Authentication, but these are disjoint sec processes
	- key to a back door gives you access without door caring who you are
	- coupons and discounts. You're authorized a discount without ID.
	- dropbox and drive allow sharing links without authenticating an ID
	- bash login as root rather than a particular user (this why often disallowed)
		- root is the user that authenticates and logs in registered users
	- authorization cookies once been authenticated.
		- if steal, authorize without authenticate
		- that's called "Session Hijacking"
		- cookies as codes that allow browser to access data, reuse without login

## Auth Providers & Pros and Cons

- OAuth as most widely used standard. OpenIDConnect is just built on OAuth 2.0
	- Pros:
		- don't have to encrypt and store user pwds (outsource auth to OAuth providers)
		- easier to register user (less friction)
		- less pwds for users to remember and you to be responsible for (e.g. leaks/site compromises)
	- Neutral:
		- need 3 party account (good if they have and like, annoying if they don't)
		- only support login via sites that are popular (cover large % of client base)
	- Cons:
		- users don't trust your site (privacy concern, e.g. posting to your FB)
		- as above, auth scopes that betray user trust (keep auth scopes minimal)
		- limited/restricted internet access
		- different auth requirements (e.g. need to change 2-factor auth or pwd strength)

## Follow the Flow

- OAuth 2.0 Playground is a Google webapp where devs can test: https://developers.google.com/oauthplayground
	- trade code for token
	- we get an access token for 3600 secs, then get list of API calls we can use

- Example OAuth 2.0 request (passing token)
	
```	
GET /userinfo/v2/me HTTP/1.1
Host: www.googleapis.com
Content-length: 0
Authorization: Bearer ya29.Glv_AwrcSLMy-oMw1dbhS9HlH4o2E1FVsuGI3nTiamE86wfeYkQqgYD1g4ahjeWU80ypa5jtIXG1WG6xZMBROdDedXTEDufnMpV9LaCvMzUR4iIgegHd4-oQBq_7
```

- Example OAuth 2.0 response
	
```
HTTP/1.1 200 OK
Content-length: 212
X-xss-protection: 1; mode=block
Content-location: https://www.googleapis.com/userinfo/v2/me
X-content-type-options: nosniff
Transfer-encoding: chunked
Expires: Mon, 01 Jan 1990 00:00:00 GMT
Vary: Origin, X-Origin
Server: GSE
-content-encoding: gzip
Pragma: no-cache
Cache-control: no-cache, no-store, max-age=0, must-revalidate
Date: Mon, 27 Feb 2017 16:23:56 GMT
X-frame-options: SAMEORIGIN
Alt-svc: quic=":443"; ma=2592000; v="35,34"
Content-type: application/json; charset=UTF-8
{
  "family_name": "", 
  "name": "", 
  "picture": "https://lh3.googleusercontent.com/-XdUIqdMkCWA/AAAAAAAAAAI/AAAAAAAAAAA/4252rscbv5M/photo.jpg", 
  "locale": "en", 
  "given_name": "", 
  "id": "117667974869561719729"
}
```
