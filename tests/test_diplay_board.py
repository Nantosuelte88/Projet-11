import pytest
from server import app, clubs

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_display_board(client):
    """
    Teste que la page et le tableau s'affichent correctement
    """
    response = client.get('/table')
    assert response.status_code == 200
    assert b'Clubs Table' in response.data
    assert b'Club' in response.data
    assert b'Points' in response.data
    assert b'Back to login page' in response.data

def test_no_clubs_display_board(client):
    """
    Teste si le message s'affiche correctement en cas de liste de "clubs" vide
    """

    # On garde la vraie liste des clubs en memoire
    existing_clubs = clubs
    # On vide la liste
    clubs.clear()

    response = client.get('/table', query_string={'clubs': None})
    assert b'Clubs Table' in response.data
    assert b'No clubs to currently display' in response.data

    # On restaure la liste des clubs
    clubs.extend(existing_clubs)
