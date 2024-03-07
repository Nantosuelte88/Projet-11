import pytest
from server import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_display_board(client):
    response = client.get('/table')
    assert response.status_code == 200
    assert b'Clubs Table' in response.data
    assert b'Back to login page' in response.data
