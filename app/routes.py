from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, getMoneyForm, GameForm, BetForm, ChooseWinnerForm, SearchForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Game, Bet
from werkzeug.urls import url_parse
from datetime import datetime


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():   
    form = getMoneyForm()

    #If the user clicks the submit button
    #add whatever amount of money they need to their acount
    if form.validate_on_submit():
        current_user.add_moola(form.ammountNeeded.data)
        db.session.commit()
        flash('Congratulations, you added money to your profile!')
        moola = round(current_user.moola, 2)
        current_user.set_moola(moola)
        return redirect(url_for('index'))
    #rounding the User's money
    moola = round(current_user.moola, 2)
    current_user.set_moola(moola)


    return render_template("index.html", title='Home Page', form=form)

@app.route('/games', methods=['GET', 'POST'])
def games():
    form = GameForm()
    search = SearchForm()
    games = Game.query.all()
    now = datetime.now()
    print(form.date.data)


     
        

    if form.validate_on_submit():
        dateOut = form.date.data
        #if the date the user enters is earlier than the current date
        #then dont let them enter it
        if now > dateOut:
            flash("ERROR: Invalid Date")
            return redirect(url_for('games'))
        #if the amount of money the user wants to bet is more than they have
        #then dont let them and reload the page
        #if not, then make a new game with all of the paramiters 
        #given by the feild
        if form.initalBetA.data > 0:
            current_user.minus_moola(form.initalBetA.data)
            if current_user.moola < 0:
                current_user.add_moola(form.initalBetA.data)
                flash("ERROR: Insuficent Funds")
                return redirect(url_for('games'))
            game = Game(userId=current_user.id, sport=form.sport.data, location=form.location.data, watchSpot=form.watchSpot.data, eventName=form.name.data, openingBetA=form.initalBetA.data, currentBetA=form.initalBetA.data, openingBetB=0, currentBetB=0, teamA= form.teamA.data , teamB= form.teamB.data, closeDate=dateOut )
        elif form.initalBetB.data > 0:
            current_user.minus_moola(form.initalBetB.data)
            if current_user.moola < 0:
                current_user.add_moola(form.initalBetB.data)
                flash("ERROR: Insuficent Funds")
                return redirect(url_for('games'))
            game = Game(userId=current_user.id, sport=form.sport.data, location=form.location.data, watchSpot=form.watchSpot.data, eventName=form.name.data, openingBetA=0, currentBetA=0, openingBetB=form.initalBetB.data, currentBetB=form.initalBetB.data, teamA= form.teamA.data , teamB= form.teamB.data, closeDate=dateOut )
       
        #if user didnt enter a starting bet for either team
        #then set both to zero
        else:
            game = Game(userId=current_user.id, sport=form.sport.data, location=form.location.data, watchSpot=form.watchSpot.data, eventName=form.name.data, openingBetA=0, currentBetA=0, openingBetB=0, currentBetB=0, teamA= form.teamA.data , teamB= form.teamB.data, closeDate=dateOut )
       
        #add the game to database
        db.session.add(game)
        db.session.commit()
        flash('Congratulations, you added a game!')
        return redirect(url_for('games')) 

    #If someone searches for something in the search bar
    #Then reload the page with a new list of games using the paramiters given
    elif search.validate_on_submit():
        games = Game.query.filter_by(sport=search.sport.data).all()
        return render_template("games.html", title='Home Page', games=games, form=form, now=now, search=search)   

    #Getting the current time of day to make sure the user 
    #doesn't enter a date for a game that has already pased
    now = datetime.now()
    return render_template("games.html", title='Home Page', games=games, form=form, now=now, search=search)




@app.route('/bet/<int:gameId>', methods=['GET', 'POST'])
def bet(gameId):
    form = BetForm()
    game = Game.query.filter_by(id=gameId).first()
    now = datetime.now()
    search = SearchForm()


    if form.validate_on_submit():

        #check if they have sufficent money
        current_user.minus_moola(form.ammountBetting.data)
        if current_user.moola < 0:
            current_user.add_moola(form.ammountBetting.data)
            flash("Insuficent Funds")
            return redirect(url_for('games')) 

        #Add the bet to the corresponding team's current bet
        elif form.teamBetting.data == game.teamA:
            game.add_betA(form.ammountBetting.data)
        elif form.teamBetting.data == game.teamB:
            game.add_betB(form.ammountBetting.data)

        #Create a new Bet in the database to keep track of who bet for who
        bet = Bet(userId=current_user.id, amountBetting=form.ammountBetting.data, teamBetting=form.teamBetting.data, gameId=gameId)
        db.session.add(bet)
        db.session.commit()
        return redirect(url_for('games'))
       
    return render_template("bet.html", title='Home Page', form=form, game=game)

@app.route('/win/<int:gameId>', methods=['GET', 'POST'])
def win(gameId):
    game = Game.query.filter_by(id=gameId).first()
    form = ChooseWinnerForm()
    games = Game.query.all()
    now = datetime.now()
    search = SearchForm()
    
    if form.validate_on_submit():

        #Check to see which of the check marks has been checked
        checkList = request.form.getlist("teams")

        #If they haven't choosen a winner
        #then reload the page and ask for one
        if checkList == []:
            flash("Please select a winner")
            return render_template("win.html", title='Home Page', game=game, form=form)


        #Checking to see which team the checkmark corresponds to
        for value in checkList:
            print(value)
            if int(value) == 1:
                winningTeam = game.teamA
            elif int(value) == 2:
                winningTeam = game.teamB

        print(winningTeam)
        #Getting all of the bets that were made using the name of the winning team
        winningBets = Bet.query.filter_by(teamBetting=winningTeam, gameId=gameId).all()
        x = 0
        winners = []
        print(winningBets)

        #Getting each user that placed a bet for the winning team (the winners)
        for bet in winningBets:
            print(bet)
            x += 1
            winners.append(bet.userId)
        print(x)

        #Getting how much money was bet for the other team
        if winningTeam == game.teamA:
            bank = game.currentBetA
        else:
            bank = game.currentBetB

        #If no one bet for the winning team to win
        #then delete the game and show an error
        if x == 0 or bank == 0:

            #If the user who created the game was the only person to bet
            #on the winning team, then I return their money.
            user = User.query.filter_by(id=game.userId).first()
            user.add_moola(bank)
            db.session.delete(game)
            db.session.commit()
            flash("ERROR: No bets made for this team")
            return redirect(url_for('games'))
        #How much money goes to each user (I have it equal for all users which i relize is not ideal however with the time constraint it will have to do)
        perUser = bank/x

        #Going through all the winners and paying them for winning
        for winner in winners:
            winningUser = User.query.filter_by(id=winner).first()
            winningUser.add_moola(perUser)

        #deleting all of the bets made so that in case there is another game created  
        #with the same team names the program won't fail
        for bet in winningBets:
            db.session.delete(bet)
        db.session.delete(game)
        db.session.commit()
        
        #reload the game page
        return redirect(url_for('games'))
      
    return render_template("win.html", title='Home Page', game=game, form=form)


#LOGIN AND LOGOUT ARE THE EXACT SAME AS BEFORE EXEPT FOR LINE 238

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():

        #set the user's money to 0 upon registration
        user = User(username=form.username.data, email=form.email.data, moola=0)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

