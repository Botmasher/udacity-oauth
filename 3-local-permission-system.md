# Local Permission System

## Intro & Implementing
- use server-side logic and db to control data based on credentials
- db must store info in a more user-specific way
	- table of Users to identify which data belongs to whom
	- Restaurant and MenuItems should track `user_id`
	- so we'll add it to both of those tables
- back-end code hooks everything together
	- `login_session[]`
	- `createUser()`

## Steps for implementing inside my Flask app

1. User table
	- name string
	- email string
	- picture string
	- id integer

2. Modify `Restaurant` and `MenuItem` classes to include `user_id`
	- in SQLAlchemy, add as foreign key
```
	user_id = Column(Integer, ForeignKey('user.id'))
```
	- in SQLAlchemy, also make sure to store relationship with user
```
	user = relationship(User)
```
	- update json properties in the models if you're serializing data:
```
	@property
	def serialize(self):
		return {
			'id': self.id,
			...
			'user': self.user
		}
```

3. Open up project file and add the `User` to the model imports
- instructor is relying on email for checking user
```
from models import Base, Restaurant, MenuItem, User
```

4. Add functions to create and get user info
```
	def createUser(login_session):
		newUser = User(name=login_session['username'],picture=login_session['picture'])
		session.add(newUser)
		session.commit()
		user = session.query(User).filter_by(email=login_session['email']).one
		return user.id

	def getUserInfo (user_id):
		user = session.query(User).filter_by(id=user_id).one()
		return user

	def getUserID (email):
		try:
			user = session.query(User).filter_by(email=email).one()
			return user.id
		except:
			return None
```

5. Now whenever you create a new `restaurant` or `menuItem`, pass `user_id` too
```
	# or whatever your route and method is
	@app.route('/restaurants/new/')
	def newRestaurant():
		# inside POST
		newRestaurant = Restaurant(name=request.form['name'],user_id=login_session['user_id'])
		# then do your add and commit
```

6. add user check to the gconnect method; automatically create new user if none exists
- *really* depends on how you set up User model
- how did you handle auth id?
```
	# see if user exists, if not make a new one
	user = session.query(User).filter_by(gplus_id=login_session['gplus_id']).one()
	if user == None:
		newUser = User(name=login_session['username'], gplus_id=login_session['gplus_id'], picture=login_session['picture'])
		session.add(newUser)
		session.commit()
	user = session.query(User).filter_by(gplus_id=login_session['gplus_id']).one()

	# add user.id to login_session for future user queries
	login_session['user_id'] = user.id

	// BETTER: refactor user check to utilize those three methods you wrote in #4
```

10. Protect menu and restaurant add/edit/delete functions
```
	// do not show the links on page to non-logged-in users
	if 'username' in login_session and login_session['user_id']==m.userId:
		output += '<a href="%s">edit</a>' % (url_for('update',...))

	// keep users from being able to post data they do not have access to through url 
	// this example uses a JS alert and was added to my update and delete methods
	if login_session['user_id'] != session.query(Restaurant).filter_by(id=index).one().userId:
		return '<script>function alertPermiss() {alert("Not authorized to update. Create a restaurant in order to update it.");}</script><body onload="alertPermiss=()">'
```

11. I had to go back through and repopulate my db, set up the forms page to work with user, and all pages to point to the new db since I renamed it to distinguish models from models with User added.