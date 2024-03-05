import json
from flask import Flask,render_template,request,redirect,flash,url_for


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

competitions = loadCompetitions()
clubs = loadClubs()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary',methods=['POST'])
def showSummary():
    club = [club for club in clubs if club['email'] == request.form['email']][0]
    return render_template('welcome.html',club=club,competitions=competitions)


@app.route('/book/<competition>/<club>')
def book(competition,club):
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = [c for c in competitions if c['name'] == competition][0]
    if foundClub and foundCompetition:
        return render_template('booking.html',club=foundClub,competition=foundCompetition)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    competition_name = request.form['competition']
    club_name = request.form['club']
    placesRequired = int(request.form['places'])

    # Trouver la compétition correspondante
    competition = next((c for c in competitions if c['name'] == competition_name), None)
    club = next((c for c in clubs if c['name'] == club_name), None)
    if competition:
        # Vérifier si le club a deja reservé des places dans cette competition
        club_competition = next((c for c in competition.get('clubs', []) if c['name'] == club_name), None)

        if club_competition:
            club_places_reserved = club_competition.get('placesReserved', 0)
        else:
            club_places_reserved = 0

        # Verifier si le nombre total de places servées apres la demande
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

    else:
        flash('Competition not found!')
    
    return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))