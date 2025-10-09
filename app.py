from flask import Flask, render_template, redirect, url_for, session, flash, request
from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length
from models import User, Chat, db
from werkzeug.security import generate_password_hash, check_password_hash
from openai import OpenAI
import os
from dotenv import load_dotenv

app = Flask(__name__)

app.config['SECRET_KEY'] = 'MYKEY'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize db
db.init_app(app)

# OpenAI client
load_dotenv()
api_key=os.environ['OPENAI_KEY_KEY']
client = OpenAI(api_key=api_key)

# Forms
class Signupform(FlaskForm):
    email = EmailField("Email:", validators=[DataRequired()])
    password = PasswordField("Password:", validators=[DataRequired(), Length(min=6)])
    con_password = PasswordField("Confirm password:", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Submit")

class Loginform(FlaskForm):
    email = EmailField("Email:", validators=[DataRequired()])
    password = PasswordField("Password:", validators=[DataRequired()])
    submit = SubmitField("Submit")

class RequestForm(FlaskForm):
    request = TextAreaField("Ask something", validators=[DataRequired()])
    submit = SubmitField("Ask")

# Routes

#login route
@app.route('/', methods=['GET', 'POST'])
def login():
    form = Loginform()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_email'] = user.email
            flash('Login successful','success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password','error')
    return render_template('login.html', form=form)

#signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = Signupform()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()

        if user:
            flash('User already exists','error')
            return redirect(url_for('login'))
        else:
            hashed_password = generate_password_hash(password)
            new_user = User(email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created','info')
            return redirect(url_for('login'))
    return render_template('signup.html', form=form)



#dashboard route
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    form = RequestForm()
    user_email = session['user_email']
    chats=Chat.query.filter_by(user_id=user_email).all()
    
    response_text = None
    if form.validate_on_submit():
        prompt = form.request.data
        # Fetch last chats for context
        
        previous_chats = Chat.query.filter_by(user_id=user_email).all()
        previous_chats = list(reversed(previous_chats))  # oldest first

        # Build message list with history
        messages = []
        for chat in previous_chats:
            messages.append({"role": "user", "content": chat.request})
            messages.append({"role": "assistant", "content": chat.response})

        # Add the current prompt
        messages.append({"role": "user", "content": prompt})

        # Call OpenAI with full context
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
         )


        response_text = response.choices[0].message.content.strip()

        new_chat = Chat(user_id=user_email, request=prompt, response=response_text)
        db.session.add(new_chat)
        db.session.commit()
         # Redirect with response as query parameter to clear POST form data
       
        return redirect(url_for('dashboard', response=response_text))

    # Get response from query string (if redirected)
    
    response_text = request.args.get('response')

    return render_template('dashboard.html', form=form, response=response_text,chat=chats)

@app.route('/history')
def history():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    user_email = session['user_email']
    chats = Chat.query.filter_by(user_id=user_email).all()
    return render_template('history.html', chats=chats)
    

@app.route('/logout')
def logout():
    session.pop('user_email', None)
    session['_flashes'] = []
    flash('You have been logged out.', 'error') 
    return redirect(url_for('login'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)





print(4)

print(8)
