import pytest
from flask.testing import FlaskClient
from flask import flash, request
from server import app, purchasePlaces, clubs, loadClubs

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def authenticate(client, email):
    with client.session_transaction() as session:
        session['email'] = email


def test_low_than_points_allowed(client, mocker):
    mocker.patch('server.competitions', [{
        'name': 'Spring Festival', 
        'date': '2025-01-01 10:00:00', 
        'numberOfPlaces': '25'
        }])

    mocker.patch('server.clubs', [{
        "name":"She Lifts",
        "email": "kate@shelifts.co.uk",
        "points":"12"
        }])


    # Authentification
    authenticate(client, 'kate@shelifts.co.uk')

    # Simuler la réservation de places pour une compétition où le club demande moins de places que de points qu'il a
    response = client.post('/purchasePlaces', data={'competition': 'Spring Festival', 'club': 'She Lifts', 'places': '10'})
    assert response.status_code == 200
    assert b"Great-booking complete! You have reserved 10 place(s)" in response.data


def test_more_than_points_allowed(client, mocker):
    places_required = 6

    mocker.patch('server.competitions', [{
        "name": "Fall Classic",
        "date": "2025-10-22 13:30:00",
        "numberOfPlaces": "13"
        }])

    mocker.patch('server.clubs', [{
        "name":"Iron Temple",
        "email": "admin@irontemple.com",
        "points":"4"
        }])

    data = {
        'competition': 'Fall Classic',
        'club': 'Iron Temple',
        'places': str(places_required)
    }

    places_not_accepted = places_required - 4
    places_accepted = places_required - places_not_accepted

    # Authentification
    authenticate(client, 'admin@irontemple.com')

    response = client.post('/purchasePlaces', data=data, follow_redirects= True)   
    response_data = response.get_data(as_text=True)

    assert places_accepted == 4

    assert f'Your points balance is insufficient; we were only able to reserve {places_accepted} places.' in response_data
