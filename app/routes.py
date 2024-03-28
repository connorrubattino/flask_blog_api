from flask import request, render_template
from . import app, db
from .models import User, Post
from .auth import basic_auth


# Define a route
@app.route("/")
def index():
    return render_template('index.html')

#user endpoints

#create new user
@app.route('/users', methods=['POST'])
def create_user():
    #check to make sure the request body is JSON
    if not request.is_json:
        return {'error': 'You content-type must be application/json'}, 400
    # Get the data from the request body
    data = request.json
    
    # Validate that the data has all of the required fields
    required_fields = ['firstName', 'lastName', 'username', 'email', 'password']
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        return {'error': f"{', '.join(missing_fields)} must be in the request body"}, 400
    #pull the individual data from the body
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    #check to see if any current users already have the username and/or email
            #in terminal - select_stmt3 = db.select(User).where(User.id > 3)   ----  select_stmt5 = db.select(User).where( (User.id > 3) | (User.username=='bstanton')  --- db.session.execute(select_stmt5).scalars().all()
            #db.session.execute(db.select(User).where( (User.username == username) | (User.email == email) )).scalars().all()
    check_users = db.session.execute(db.select(User).where( (User.username == username) | (User.email == email) )).scalars().all()
    if check_users:
        return {'error': "A user with that username and/or email already exists"}, 400

    #create a new instance of user with the data rom the request
    new_user = User(first_name=first_name, last_name=last_name,  username=username, email=email, password=password)

    return new_user.to_dict(), 201


@app.route('/token')
@basic_auth.login_required
def get_token():
    user = basic_auth.current_user()
    return user.get_token()




#post endpoints

#get all posts
@app.route('/posts')
def get_posts():
    select_stmt = db.select(Post)
    search = request.args.get('search')
    if search:
        select_stmt = select_stmt.where(Post.title.ilike(f"%{search}%"))
    # Get the posts from the database
    posts = db.session.execute(select_stmt).scalars().all()
    return [p.to_dict() for p in posts]  #list comprehension calling to_dict and looping thru all posts to get them

    #get a single post by ID
@app.route('/posts/<int:post_id>')
def get_post(post_id):
    # Get the post from the database by ID
    post = db.session.get(Post, post_id)
    if post:
        return post.to_dict()
    else:
        return {'error': f"Post with an ID of {post_id} does not exist"}, 404

#Create a Post
@app.route('/posts', methods=['POST']) # same url but depending on if you are making a get request or in this case a get request it will vary in what it returns
def create_post():
    #check if the request body is JSON
    if not request.is_json:
        return {'error': 'Your content-type must be application/json'}, 400
    #get the data from the request body
    data = request.json
    #validate the incoming data
    required_fields = ['title', 'body']
    missing_fields = []
    # For each of the required fields
    for field in required_fields:
        # If the field is not in the request body dictionary
        if field not in data:
            # Add that field to the list of missing fields
            missing_fields.append(field)
    # If there are any missing fields, return 400 status code with the missing fields listed
    if missing_fields:
        return {'error': f"{', '.join(missing_fields)} must be in the request body"}, 400
    
    # Get data values
    title = data.get('title')
    body = data.get('body')

    # Create a new post instance with data (and hard code in user id for time being)
    new_post = Post(title=title, body=body, user_id=1)
    

    # Return the newly created post dictionary with a 201 Created Status Code
    return new_post.to_dict(), 201