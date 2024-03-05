import pytest
from flask.testing import FlaskClient
from flask import flash, request
from server import app, purchasePlaces, competitions, MAX_PLACES


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# Données de test
competition_name = 'Spring Festival'
club_name = 'Simply Lift'

initial_competition = next((c for c in competitions if c['name'] == competition_name), None)
initial_places = int(initial_competition['numberOfPlaces'])


def update_points(competition_name):
    # Décompte des places restantes dans la compétition après réservation
    updated_competition = next((c for c in competitions if c['name'] == competition_name), None)
    updated_places = int(updated_competition['numberOfPlaces'])
    return updated_places

def test_club_booking_limit_lower_limit(client, monkeypatch):
    places_required = 5

    # mock des données de la requête PÖST
    data = {
        'competition': competition_name,
        'club': club_name,
        'places': str(places_required)
    }

    response = client.post('/purchasePlaces', data=data, follow_redirects= True)

    updated_places = update_points(competition_name)

    remaining_places = initial_places - places_required

    response_data = response.get_data(as_text=True)

    assert f'Great-booking complete! You have reserved {places_required} place(s)' in response_data
    
    updated_competition = next((c for c in competitions if c['name'] == competition_name), None)
    club_competition = next((c for c in updated_competition.get('clubs', []) if c['name'] == club_name), None)
    places_reserved_after = club_competition['placesReserved']
    assert places_reserved_after == places_required
    
    assert updated_places == remaining_places

def test_club_limit_upper_limit(client, monkeypatch):
    places_required = 20

    data = {
        'competition': competition_name,
        'club': club_name,
        'places': str(places_required)
    }

    # Exécution de la requête POST
    response = client.post('/purchasePlaces', data=data, follow_redirects=True)

    updated_places = update_points(competition_name)

    places_not_accepted = max(places_required - MAX_PLACES, 0)
    places_accepted = places_required - places_not_accepted
    remaining_places = initial_places - places_accepted


    updated_competition = next((c for c in competitions if c['name'] == competition_name), None)
    club_competition = next((c for c in updated_competition.get('clubs', []) if c['name'] == club_name), None)
    places_reserved_after = club_competition['placesReserved']

    assert places_reserved_after == places_accepted
    assert updated_places == remaining_places
    assert remaining_places == 13
    assert places_accepted == 12

def test_multiple_bookings(client, monkeypatch):
    # Première réservation : 10 places
    places_required_first_booking = 10
    competition_places = 25

    data_first_booking = {
        'competition': competition_name,
        'club': club_name,
        'places': str(places_required_first_booking)
    }

    # Première réservation
    response_first_booking = client.post('/purchasePlaces', data=data_first_booking, follow_redirects=True)

    # Vérifier le statut de la première réservation
    assert response_first_booking.status_code == 200

    # Vérifier les données mises à jour après la première réservation
    competition_places -= places_required_first_booking

    remaining_places_first_booking = initial_places - places_required_first_booking

    # Vérifier si les places restantes sont correctes après la première réservation
    assert competition_places == remaining_places_first_booking

    # Deuxième réservation : 5 places
    places_required_second_booking = 5

    data_second_booking = {
        'competition': competition_name,
        'club': club_name,
        'places': str(places_required_second_booking)
    }

    # Deuxième réservation
    response_second_booking = client.post('/purchasePlaces', data=data_second_booking, follow_redirects=True)

    # Vérifier le statut de la deuxième réservation
    assert response_second_booking.status_code == 200

    # Vérifier les données mises à jour après la deuxième réservation
    total_places_required = places_required_first_booking + places_required_second_booking
    places_not_accepted = total_places_required - MAX_PLACES
    accepted_places = places_required_second_booking - places_not_accepted
    updated_places_second_booking = competition_places - accepted_places
    competition_places -= updated_places_second_booking

    remaining_places_second_booking = remaining_places_first_booking - updated_places_second_booking
    total_places_accepted = total_places_required - places_not_accepted
    # Vérifier si les places restantes sont correctes après la deuxième réservation
    assert competition_places == remaining_places_second_booking
    assert total_places_accepted == 12
