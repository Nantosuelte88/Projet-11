import json
from flask import Flask, render_template, request, redirect, flash, url_for, session
from flask_session import Session
from functools import wraps
from datetime import datetime

# Le nombre maximum de places pouvant être accordées à un club pour une compétition
MAX_PLACES = 12

def loadClubs():
    """
    Charge les clubs à partir du fichier clubs.json
    """
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    """
    Charge les competitions à partir du fichier competitions.json
    """
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions

# Création d'une instance de l'application Flask et définition de la clé secrète pour les cookies de session
app = Flask(__name__)
app.secret_key = 'something_special'

# Configuration et initialisation de la gestion des sessions avec le stockage sur le système de fichiers
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

def to_datetime(date_string):
    """
    Convertit une chaîne de caractères en objet datetime.
    """
    return datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")

# Passer la fonction to_datetime au modèle Jinja2
app.jinja_env.filters['to_datetime'] = to_datetime

competitions = loadCompetitions()
clubs = loadClubs()

def login_required(f):
    """
    Décorateur pour vérifier si l'utilisateur est connecté avant d'accéder à une page protégée.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session:
            flash("You need to be logged in to access this page.", "error")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

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
    
    session['email'] = email

    return render_template('welcome.html', club=club, competitions=competitions, date_today=date_today)

@app.route('/book/<competition>/<club>')
@login_required
def book(competition, club):
    """
    Affiche les competitions et verifie que la date de celle-ci soit bonne pour pouvoir reserver
    """
    date_today = datetime.today().date()
    foundClub = next((c for c in clubs if c['name'] == club), None)
    foundCompetition = next((c for c in competitions if c['name'] == competition), None)
    if foundClub and foundCompetition:
        competition_date = datetime.strptime(foundCompetition['date'], '%Y-%m-%d %H:%M:%S').date()

        # Vérification de la date de la compétition pour autoriser la réservation
        if competition_date > datetime.today().date():
            return render_template('booking.html',club=foundClub,competition=foundCompetition)
        else:
            flash("this competition has already passed")
            return render_template('welcome.html', club=club, competitions=competitions, date_today=date_today)

    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions, date_today=date_today)
    
@app.route('/purchasePlaces',methods=['POST'])
@login_required
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
    
    if competition and club:
        # Obtient le nombre de points du club
        club_points = int(club['points'])
        competition_places = int(competition['numberOfPlaces'])

        # On verifie le nombre de places disponibles dans la competition
        if competition_places <= 0:
            flash('No more places available in this competition.')
        else:

            if placesRequired <= 0:
                flash('Please enter a valid number.')
            else:

                # Si le nombre de places demandées est superieur au nombre de places encore disponibles dans la competition, 
                # on reduit le nombre de places demandées
                if placesRequired > competition_places:
                    places_not_available = placesRequired - competition_places
                    placesRequired -= places_not_available

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
@login_required
def logout():
    """
    Pour se déconnecter
    """
    session.pop('email', None) # Supprime l'email de la session
    return redirect(url_for('index'))
