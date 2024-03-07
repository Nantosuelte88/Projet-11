import pytest
from flask.testing import FlaskClient
from flask import flash, request
from server import app, purchasePlaces, clubs, loadClubs

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# Données de test
competition_name = 'Fall Classic'

def test_low_than_points_allowed(client, monkeypatch):
    places_required = 5
    # Utilisez monkeypatch pour modifier la fonction loadClubs() dans le test
    def mock_load_clubs():
        club = {'name': 'She Lifts', 'points': '12'}
        return [club]

    monkeypatch.setattr('server.loadClubs', mock_load_clubs)
    
    data = {
        'competition': competition_name,
        'club': 'She Lifts',
        'places': str(places_required)
    }

    response = client.post('/purchasePlaces', data=data, follow_redirects= True)   
    response_data = response.get_data(as_text=True)

    updated_points = int(mock_load_clubs()[0]['points']) - places_required

    # Verification des points mis à jour dans le club, 12 - 5 = 7
    assert updated_points == 7

    assert f'Great-booking complete!' in response_data

def test_more_than_points_allowed(client, monkeypatch):
    places_required = 15

    # Utilisez monkeypatch pour modifier la fonction loadClubs() dans le test
    def mock_load_clubs():
        club = {'name': 'Simply Lift', 'points': '13'}
        return [club]

    monkeypatch.setattr('server.loadClubs', mock_load_clubs)

    data = {
        'competition': competition_name,
        'club': 'Simply Lift',
        'places': str(places_required)
    }

    places_not_accepted = places_required - int(mock_load_clubs()[0]['points'])
    places_accepted = places_required - places_not_accepted

    response = client.post('/purchasePlaces', data=data, follow_redirects= True)   
    response_data = response.get_data(as_text=True)

    assert places_accepted == int(mock_load_clubs()[0]['points'])
    assert places_accepted == 13

    assert f'Your points balance is insufficient; we were only able to reserve {places_accepted} points.' in response_data
