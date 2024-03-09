import json
from flask import Flask,render_template,request,redirect,flash,url_for
from datetime import datetime


MAX_PLACES = 12

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
    # Récupérer la date du jour
    date_today = datetime.today().date()
    email = request.form['email']

    if not email:
        flash("The email cannot be empty.", "error")
        return redirect(url_for('index'))

    club = next((club for club in clubs if club['email'] == request.form['email']), None)
    if club is None:
        flash("the email isn't found.", "error")
        return redirect(url_for('index'))
    
    return render_template('welcome.html', club=club, competitions=competitions, date_today=date_today)

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
    competition_name = request.form['competition']
    club_name = request.form['club']
    placesRequired = int(request.form['places'])

    # Trouver la compétition correspondante
    competition = next((c for c in competitions if c['name'] == competition_name), None)
    club = next((c for c in clubs if c['name'] == club_name), None)
    club_points = int(club['points'])
    if competition and club:
        # Vérifier si le club a deja reservé des places dans cette competition
        club_competition = next((c for c in competition.get('clubs', []) if c['name'] == club_name), None)

        if club_competition:
            club_places_reserved = club_competition.get('placesReserved', 0)
        else:
            club_places_reserved = 0

        # Verifier si le nombre total de places reservées apres la demande
        total_club_places = club_places_reserved + placesRequired

        # Verifier si le nombre total de places servées depasse le maximum de places
        if total_club_places > MAX_PLACES:
            # Réduire le nombres de places voulues pour respecter la limite
            placesRequired = MAX_PLACES - club_places_reserved
            flash(f'You can only reserve up to {placesRequired} places due to the maximum limit of 12 places!')

        # Mettre à jour le nombre de places reservées pour le club dans la competition
        if not club_competition:
            club_competition = {'name': club_name, 'placesReserved': 0}
            competition.setdefault('clubs', []).append(club_competition)
        club_competition['placesReserved'] += placesRequired
        competition['numberOfPlaces'] = int(competition['numberOfPlaces']) - placesRequired
        flash(f'Great-booking complete! You have reserved {placesRequired} place(s)')
        if placesRequired > club_points or placesRequired == 0:
            points_not_accorded = placesRequired - club_points
            rest_points = placesRequired - points_not_accorded
            if rest_points > 0:
                flash(f'Your points balance is insufficient; we were only able to reserve {rest_points} points.')
                club['points'] = int(club['points']) - rest_points
                competition['numberOfPlaces'] = int(competition['numberOfPlaces']) - rest_points

            elif rest_points <= 0:
                flash(f'Your points balance is insufficient;')
        else:
            club['points'] = int(club['points']) - placesRequired
            competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired

            flash('Great-booking complete!')

        if int(competition['numberOfPlaces']) >= placesRequired:
            # Deduct places from the competition
            competition['numberOfPlaces'] = int(competition['numberOfPlaces']) - placesRequired
            # Deduct points from the club
            club['points'] = str(int(club['points']) - placesRequired)
            flash('Great-booking complete!')
        else:
            flash('Not enough places available for booking!')

    else:
        flash('Competition or club not found!')
    return render_template('welcome.html', club=club, competitions=competitions, date_today=date_today)

# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))