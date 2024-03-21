from flask.testing import FlaskClient
from server import app, purchasePlaces

def test_points_updated():
    client = app.test_client()

    # Les données de test
    data = {
        'competition': 'Spring Festival',
        'club': 'Simply Lift',
        'places': '5'
    }

    # Points des clubs avant l'achat
    initial_points = {
        'Simply Lift': 13,
        'Iron Temple': 4,
        'She Lifts': 12
    }

    # Les données de test
    with app.test_request_context('/purchasePlaces', method='POST', data={'competition': 'Spring Festival', 'club': 'Simply Lift', 'places': '5'}):
        purchasePlaces()

    # Vérifiez si les points ont été correctement mis à jour pour le club "Simply Lift"
    assert initial_points['Simply Lift'] - 5 == 8

    # Vérifiez si les points des autres clubs n'ont pas été modifiés
    for club, points in initial_points.items():
        if club != 'Simply Lift':
            assert points == initial_points[club]
