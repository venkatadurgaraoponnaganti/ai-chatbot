from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    email = db.Column(db.String, primary_key=True)
    password = db.Column(db.String)
    chats = db.relationship('Chat', backref='user')


    def __init__(self, email, password):
        self.email = email
        self.password = password

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('user.email'))
    request = db.Column(db.Text)
    response = db.Column(db.Text)

    def __init__(self, user_id, request, response):
        self.user_id = user_id
        self.request = request
        self.response = response