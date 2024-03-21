import pytest
from flask import Flask
from server import app

@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client

def authenticate(client, email):
    with client.session_transaction() as session:
        session['email'] = email

def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Welcome to the GUDLFT Registration Portal!" in response.data

def test_show_summary_route(client):
    response = client.post('/showSummary', data={'email': 'john@simplylift.co'})
    assert response.status_code == 200
    assert b"Welcome" in response.data

def test_book_route(client):
    response = client.get('/book/Spring Festival/Simply Lift', follow_redirects= True)
    assert response.status_code == 200 
    assert b"Welcome" in response.data

def test_purchase_places_route(client):
    # Authentification
    authenticate(client, 'john@simplylift.co')

    response = client.post('/purchasePlaces', 
                           data={'competition': 'Spring Festival', 'club': 'Simply Lift', 'places': '2'}, 
                           follow_redirects= True)
    assert response.status_code == 200
    assert b"Great-booking complete! You have reserved 2 place(s)" in response.data

def test_display_board_route(client):
    response = client.get('/table')
    assert response.status_code == 200
    assert b"Clubs Table" in response.data
    assert b"Club" in response.data
    assert b"Points" in response.data


def test_logout_route(client):
    response = client.get('/logout')
    assert response.status_code == 302
    assert response.headers['Location'] == '/'