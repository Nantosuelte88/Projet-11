import json
from flask import Flask, render_template, request, redirect, flash,url_for
from datetime import datetime

# Le nombre maximum de places pouvant être accordées à un club pour une compétition
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
    """
    Affiche la page de connexion
    """
    return render_template('index.html')

@app.route('/showSummary',methods=['POST'])
def showSummary():
    """
    Vérifie l'email, si il est correct affiche la page d'accueil, sinon redirige vers la page de connexion
    """
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
def book(competition, club):
    """
    Affiche les competitions et verifie que la date de celle-ci soit bonne pour pouvoir reserver
    """
    date_today = datetime.today().date()
    foundClub = next((c for c in clubs if c['name'] == club), None)
    foundCompetition = next((c for c in competitions if c['name'] == competition), None)
    if foundClub and foundCompetition:
        competition_date = datetime.strptime(foundCompetition['date'], '%Y-%m-%d %H:%M:%S').date()

        # Si la date de la compétition est supérieur à la date actuelle alors on peut acceder à la reservation
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
    """
    Permet de réserver une/des place.s pour une competition, sous certaines conditions
    """
    # Récupère la date du jour, le nom de la compétition, le nom du club et le nombre de places demandées
    date_today = datetime.today().date()
    competition_name = request.form['competition']
    club_name = request.form['club']
    placesRequired = int(request.form['places'])

    # Trouver la compétition correspondante
    competition = next((c for c in competitions if c['name'] == competition_name), None)
    club = next((c for c in clubs if c['name'] == club_name), None)
    # Obtient le nombre de points du club
    club_points = int(club['points'])
    
    if competition and club:
        if placesRequired <= 0:
            flash('Please enter a valid number.')
        else:
            # Verification des places demandées et des points du club
            if club_points <= 0:
                flash('You have no more points.')
            else:
                # Si le nombre de places demandées est supérieur au nombre de points du club
                if placesRequired > club_points:
                    # Calcule le nombre de places demandées en trop
                    places_not_accorded = placesRequired - club_points
                    # Calcule les places qui pourraient être accordées
                    placesRequired = placesRequired - places_not_accorded

                    if placesRequired <= 0:
                        flash(f'Your points balance is insufficient;')
                    else:
                        flash(f'Your points balance is insufficient; we were only able to reserve {placesRequired} places.')

                # Vérifie si le club a déjà réservé des places dans cette compétition
                club_competition = next((c for c in competition.get('clubs', []) if c['name'] == club_name), None)
                if club_competition:
                    # Si le club a déjà réservé des places, récupère le nombre de places déjà réservées
                    club_places_reserved = club_competition.get('placesReserved', 0)
                else:
                    # Si le club n'a pas encore réservé de places, initialise le nombre de places réservées à 0
                    club_places_reserved = 0

                # Calcule le nombre total de places après la demande
                total_club_places = club_places_reserved + placesRequired

                # Vérifie si le nombre total de places réservées dépasse le maximum de places
                if total_club_places > MAX_PLACES:
                    # Réduit le nombre de places souhaitées pour respecter la limite
                    placesRequired = MAX_PLACES - club_places_reserved
                    flash(f'You can only reserve up to {placesRequired} places due to the maximum limit of 12 places per competition!')

                # Met à jour le nombre de places réservées pour le club dans la compétition
                if not club_competition:
                    # Si le club n'a pas encore réservé de places dans cette compétition
                    # Crée un nouvel enregistrement pour le club avec le nombre de places réservées initialisé à 0
                    club_competition = {'name': club_name, 'placesReserved': 0}
                    # Ajoute le nouvel enregistrement du club à la liste des clubs de la compétition
                    competition.setdefault('clubs', []).append(club_competition)

                if placesRequired > 0:
                    club_competition['placesReserved'] += placesRequired

                    # Met à jour les points du club ainsi que le nombre de places de la compétition
                    club['points'] = int(club['points']) - placesRequired
                    competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired
                    
                    flash(f'Great-booking complete! You have reserved {placesRequired} place(s)')

    else:
        flash('Competition or club not found!')
    return render_template('welcome.html', club=club, competitions=competitions, date_today=date_today)

# TODO: Add route for points display
@app.route('/table')
def displayBoard():
    """
    Affiche un tableau des clubs avec leurs points, si aucun club n'est chargé on affiche un message
    """
    if not clubs:
        flash('No clubs to currently display')
    return render_template('table.html', clubs=clubs)

@app.route('/logout')
def logout():
    """
    Pour se déconnecter
    """
    return redirect(url_for('index'))