from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User
from wtforms.fields.html5 import DateTimeLocalField

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

#Letting the user create a game
class GameForm(FlaskForm):
    sport = StringField('Sport', validators=[DataRequired()])
    location = StringField('Location')
    watchSpot = StringField('Where to Watch')
    name = StringField('Event Name')
    initalBetA = IntegerField('Inital Bet Team 1') 
    initalBetB = IntegerField('Inital Bet Team 2')
    submit = SubmitField('Submit')
    teamA = StringField('1st Team', validators=[DataRequired()])
    teamB = StringField('2nd Team', validators=[DataRequired()])
    date = DateTimeLocalField('When does the event end?', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])

#Letting the user bet on games
class BetForm(FlaskForm):
    ammountBetting = IntegerField('Amount Betting', validators=[DataRequired()])
    teamBetting = StringField('Team Name', validators=[DataRequired()])
    submit = SubmitField('Submit') 

#Adding money to the user's account
class getMoneyForm(FlaskForm):
    ammountNeeded = IntegerField('Ammount Needed $', validators=[DataRequired()])
    submit = SubmitField('Submit')

#Choosing the winner
class ChooseWinnerForm(FlaskForm):
    #Checking the checkbox to see if it's checked or not
    save = SubmitField("Save Winner")

#Searching for a sport to filter games by
class SearchForm(FlaskForm):
    sport = StringField('Search for a sport:', validators=[DataRequired()])
    search = SubmitField('Search')
    