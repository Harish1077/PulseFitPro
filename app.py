
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'devsecret')
from dotenv import load_dotenv
load_dotenv()
POSTGRES_URL = os.environ.get('DATABASE_URL') or \
    f"postgresql://{os.environ.get('POSTGRES_USER', 'pulsefit')}:{os.environ.get('POSTGRES_PASSWORD', 'pulsefitpass')}@{os.environ.get('POSTGRES_HOST', 'db')}:{os.environ.get('POSTGRES_PORT', '5432')}/{os.environ.get('POSTGRES_DB', 'pulsefit')}"
app.config['SQLALCHEMY_DATABASE_URI'] = POSTGRES_URL if os.environ.get('USE_POSTGRES', '1') == '1' else 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# Models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    workouts = db.relationship('Workout', backref='owner', lazy=True)

class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exercise = db.Column(db.String(100), nullable=False)
    calories = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # duration in minutes
    notes = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Forms
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=150)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class WorkoutForm(FlaskForm):
    exercise = StringField('Workout Name', validators=[DataRequired()])
    calories = IntegerField('Calories Burned', validators=[DataRequired(), NumberRange(min=1)])
    duration = IntegerField('Duration (minutes)', validators=[DataRequired(), NumberRange(min=1)])
    notes = StringField('Notes (optional)')
    submit = SubmitField('Add Workout')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
@login_required
def home():
    workouts = Workout.query.filter_by(owner=current_user).order_by(Workout.date.desc()).all()
    return render_template("index.html", workouts=workouts, form=WorkoutForm())


@app.route("/add", methods=["POST"])
@login_required
def add_workout():
    form = WorkoutForm()
    if form.validate_on_submit():
        workout = Workout(
            exercise=form.exercise.data,
            calories=form.calories.data,
            duration=form.duration.data,
            notes=form.notes.data,
            owner=current_user
        )
        db.session.add(workout)
        db.session.commit()
        flash('Workout added!', 'success')
    else:
        flash('Invalid input.', 'danger')
    return redirect(url_for('home'))

# Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Login failed. Check email and password.', 'danger')
    return render_template('login.html', form=form)

# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)