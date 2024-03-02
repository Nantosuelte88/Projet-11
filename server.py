import json
from flask import Flask,render_template,request,redirect,flash,url_for
from datetime import datetime


def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

# Définition d'une fonction pour convertir une chaîne de caractères en objet datetime
def to_datetime(date_string):
    return datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")

# Passer la fonction to_datetime au modèle Jinja2
app.jinja_env.filters['to_datetime'] = to_datetime

competitions = loadCompetitions()
clubs = loadClubs()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary',methods=['POST'])
def showSummary():
    club = [club for club in clubs if club['email'] == request.form['email']][0]
    # Récupérer la date du jour
    date_today = datetime.today().date()
    return render_template('welcome.html',club=club,competitions=competitions,date_today=date_today)


@app.route('/book/<competition>/<club>')
def book(competition,club):
    date_today = datetime.today().date()
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = next((c for c in competitions if c['name'] == competition), None)
    if foundClub and foundCompetition:
        competition_date = datetime.strptime(foundCompetition['date'], '%Y-%m-%d %H:%M:%S').date()
        print(foundCompetition, 'date:', competition_date)
        if competition_date > datetime.today().date():
            return render_template('booking.html',club=foundClub,competition=foundCompetition)
        else:
            flash("this competition has already passed")
            return render_template('welcome.html', club=club, competitions=competitions, date_today=date_today)

    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions, date_today=date_today)


@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    date_today = datetime.today().date()
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    placesRequired = int(request.form['places'])
    competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired
    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions, date_today=date_today)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))