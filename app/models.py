from datetime import datetime
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    moola = db.Column(db.Integer)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    #Functions to manipulate the money for each user
    def add_moola(self, moola):
        self.moola += moola

    def minus_moola(self, moola):
        self.moola -= moola

    def set_moola(self, moola):
        self.moola = moola


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'))
    sport = db.Column(db.String(30))
    location = db.Column(db.String(120))
    watchSpot = db.Column(db.String(60))
    eventName = db.Column(db.String(90))
    openingBetA = db.Column(db.Integer)
    openingBetB = db.Column(db.Integer)
    currentBetA = db.Column(db.Integer)
    currentBetB = db.Column(db.Integer)
    teamA = db.Column(db.String(30))
    teamB = db.Column(db.String(30))
    closeDate = db.Column(db.DateTime)

    #Manipulating bets
    def add_betA(self, bet):
        self.currentBetA += bet

    def add_betB(self, bet):
        self.currentBetB += bet



class Bet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'))
    amountBetting = db.Column(db.Integer)
    teamBetting = db.Column(db.String(30))
    gameId = db.Column(db.Integer, db.ForeignKey('game.id'))


@login.user_loader
def load_user(id):
    return User.query.get(int(id))