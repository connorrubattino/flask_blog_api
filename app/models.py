import secrets
from . import db   #can also be from app import db
from datetime import datetime, timezone, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    posts = db.relationship('Post', back_populates='author') #matching inverse of below in post is connecting them in pyhton with relationship -- foriegn keys are for database
    token = db.Column(db.String, index=True, unique=True)
    token_expiration = db.Column(db.DateTime(timezone=True))
    comments = db.relationship('Comment', back_populates='user')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_password(kwargs.get('password', '')) #find the password in args

    def __repr__(self):
        return f"<User {self.id}|{self.username}>"
    
    def set_password(self, plaintext_password):
        self.password = generate_password_hash(plaintext_password)
        self.save()

    def save(self): #to add to the database automatically like done in the terminal
        db.session.add(self)
        db.session.commit()

    def check_password(self, plaintext_password):
        return check_password_hash(self.password, plaintext_password)
    
    #turn the User into a dict type
    def to_dict(self):
        return {
            "id": self.id,
            "firstName": self.first_name,
            "lastName": self.last_name,
            "username": self.username,
            "email": self.email,
            "dateCreated": self.date_created
        }

    def get_token(self):
        now = datetime.now(timezone.utc)
        if self.token and self.token_expiration > now + timedelta(minutes=1):
            return {"token": self.token, "tokenExpiration": self.token_expiration}
        self.token = secrets.token_hex(16)
        self.token_expiration = now + timedelta(hours=1)
        self.save()
        return {"token": self.token, "tokenExpiration": self.token_expiration}


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    body = db.Column(db.String, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    # In SQL - user_id INTEGER NOT NULL, FOREIGN KEY(user_id) REFERENCES user(id) -- 'user.id' below takes id from user table
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', back_populates='posts')  #matching inverse of up in User
    comments = db.relationship('Comment', back_populates='post')

                    #anytime the database models change (new tables or column) must rerun flask db migrate -m""" and upgrade
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.save()

    def __repr__(self):
        return f"<Post {self.id}|{self.title}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "body": self.body,
            "dateCreated": self.date_created,
            "author": self.author.to_dict(), #brings in the user of the post so you can see it along with the post
            "comments": [comment.to_dict() for comment in self.comments]
        }       

    def update(self, **kwargs):
        allowed_fields = {'title', 'body'}

        for key, value in kwargs.items():
            if key in allowed_fields:  
                setattr(self, key, value) 
        self.save() 

    def delete(self):
        db.session.delete(self) # deleting THIS object from the database
        db.session.commit() # commiting our changes



# Create our Comment class/table
class Comment(db.Model):
    # CREATE TABLE
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    post = db.relationship('Post', back_populates='comments')
    user = db.relationship('User', back_populates='comments')

    # INSERT INTO
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.save()

    def __repr__(self):
        return f"<Comment {self.id}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        return {
            'id': self.id,
            'body': self.body,
            'dateCreated': self.date_created,
            'post_id': self.post_id,
            'user': self.user.to_dict()
        }