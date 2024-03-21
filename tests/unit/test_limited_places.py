import pytest
from flask.testing import FlaskClient
from flask import flash, request
from server import app, purchasePlaces, competitions, MAX_PLACES, clubs


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def authenticate(client, email):
    with client.session_transaction() as session:
        session['email'] = email

def test_club_booking_limit_lower_limit(client, mocker):
    places_required = 6

    competitions_data = [{
        "name": "Fall Classic",
        "date": "2025-10-22 13:30:00",
        "numberOfPlaces": "13"
    }]

    clubs_data = [{
        "name": "She Lifts",
        "email": "kate@shelifts.co.uk",
        "points": "12"
    }]

    mocker.patch('server.competitions', competitions_data)
    mocker.patch('server.clubs', clubs_data)

    data = {
        'competition': 'Fall Classic',
        'club': 'She Lifts',
        'places': str(places_required)
    }

    # Authentification
    authenticate(client, 'kate@shelifts.co.uk')


    # Simuler la réservation de places pour une compétition où le club demande moins de places que de points qu'il a
    response = client.post('/purchasePlaces', data=data, follow_redirects= True)
    assert response.status_code == 200
    assert b"Great-booking complete! You have reserved 6 place(s)" in response.data

    # Vérification que le club a maintenant 7 places (13 - 6)
    updated_competition = next((c for c in competitions_data if c['name'] == 'Fall Classic'), None)
    assert updated_competition['numberOfPlaces'] == 7

def test_club_limit_upper_limit(client, mocker):
    places_required = 13

    competitions_data = [{
        "name": "Fall Classic",
        "date": "2025-10-22 13:30:00",
        "numberOfPlaces": "13"
        }]

    clubs_data = [{
        "name": "Simply Lift",
        "email": "john@simplylift.co",
        "points":"13"
        }]
    
    mocker.patch('server.competitions', competitions_data)
    mocker.patch('server.clubs', clubs_data)

    data = {
        'competition': 'Fall Classic',
        'club': "Simply Lift",
        'places': str(places_required)
    }

    # Authentification
    authenticate(client, 'john@simplylift.co')

    # on compte les places non acceptées 13 - 12 = 1
    places_not_accepted = places_required - MAX_PLACES
    places_accepted = places_required - places_not_accepted

    # Exécution de la requête POST
    response = client.post('/purchasePlaces', data=data, follow_redirects=True)
    assert response.status_code == 200

    assert b'You can only reserve up to 12 places due to the maximum limit of 12 places per competition!' in response.data

    # Vérification que le club a maintenant 1 places (13 - 12)
    updated_competition = next((c for c in competitions_data if c['name'] == 'Fall Classic'), None)
    assert updated_competition['numberOfPlaces'] == 1

def test_multiple_bookings(client, mocker):
    places_required_first_booking = 10

    competitions_data = [{
        "name": "Spring Festival",
        "date": "2025-03-27 10:00:00",
        "numberOfPlaces": "25"
        }]

    clubs_data = [{
        "name": "Simply Lift",
        "email": "john@simplylift.co",
        "points":"13"
        }]
    
    mocker.patch('server.competitions', competitions_data)
    mocker.patch('server.clubs', clubs_data)

    data_first_booking = {
        'competition': 'Spring Festival',
        'club': "Simply Lift",
        'places': str(places_required_first_booking)
    }

    # Authentification
    authenticate(client, 'john@simplylift.co')

    # Première réservation
    response_first_booking = client.post('/purchasePlaces', data=data_first_booking, follow_redirects=True)

    # Vérifier le statut de la première réservation
    assert response_first_booking.status_code == 200
    assert b"Great-booking complete! You have reserved 10 place(s)" in response_first_booking.data


    # Vérification que le club a maintenant 15 places (25 - 10)
    updated_competition = next((c for c in competitions_data if c['name'] == 'Spring Festival'), None)
    assert updated_competition['numberOfPlaces'] == 15

    # Deuxième réservation : 3 places
    places_required_second_booking = 3

    data_second_booking = {
        'competition': 'Spring Festival',
        'club': "Simply Lift",
        'places': str(places_required_second_booking)
    }

    # Deuxième réservation
    response_second_booking = client.post('/purchasePlaces', data=data_second_booking, follow_redirects=True)

    # Vérifier le statut de la deuxième réservation
    assert response_second_booking.status_code == 200
    assert b'You can only reserve up to 2 places due to the maximum limit of 12 places per competition!' in response_second_booking.data

    # Vérifier les données mises à jour après la deuxième réservation
    total_places_required = places_required_first_booking + places_required_second_booking # 10 + 3
    places_not_accepted = total_places_required - MAX_PLACES # 13 - 12

    # Vérification que le club a maintenant 13 places (15 - 2)
    updated_competition = next((c for c in competitions_data if c['name'] == 'Spring Festival'), None)
    assert updated_competition['numberOfPlaces'] == 13