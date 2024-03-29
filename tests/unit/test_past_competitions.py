import pytest
from server import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def authenticate(client, email):
    with client.session_transaction() as session:
        session['email'] = email

def test_book_valid_date(client, mocker):
    """
    Teste la réservation pour une date de competition valide
    """
    mocker.patch('server.competitions', [{
        'name': 'Spring Festival', 
        'date': '2025-01-01 10:00:00', 
        'numberOfPlaces': '25'
        }])
    
    # Authentification
    authenticate(client, 'john@simplylift.co')

    response = client.get('/book/Spring Festival/Simply Lift')
    assert response.status_code == 200

def test_book_valid_date_already_passed(client, mocker):
    """
    Teste la réservation pour une date de competition invalide (deja passée)
    """
    mocker.patch('server.competitions', [{
        'name': 'Past Competition', 
        'date': '2021-01-01 10:00:00', 
        'numberOfPlaces': '25'
        }])
    
    # Authentification
    authenticate(client, 'john@simplylift.co')

    response = client.get('/book/Past Competition/Simply Lift')
    assert response.status_code == 200
    assert b"This competition has already passed" in response.data

def test_book_invalid_competition(client, mocker):
    """
    Teste la réservation pour une competition invalide
    """
    mocker.patch('server.competitions', [])

    # Authentification
    authenticate(client, 'john@simplylift.co')

    response = client.get('/book/Invalid Competition/Simply Lift')
    assert response.status_code == 200
    assert b"Something went wrong-please try again" in response.data
    