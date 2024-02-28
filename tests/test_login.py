import pytest
from flask import Flask, render_template
from server import app

from server import index, showSummary

@pytest.fixture
def client():
    app.config['TESTING'] = True #activer le mode de test de Flask
    with app.test_client() as client: #créer un client de test
        yield client #retourner le client

def test_should_status_code_ok(client):
    """
    Teste la route d'accueil ('/') de l'application Flask.

    Vérifie si la page d'accueil renvoie le bon modèle de rendu 'index.html'.
    """
    response = client.get('/')
    assert response.status_code == 200
    assert response.data.decode('utf-8') == render_template('index.html')


# Test sur les emails en connexion  
def test_showSummary_empty_email(client):
    """
    Teste si l'email est vide.

    Si l'email est vide il redirige vers la page "index".
    """
    response = client.post('/showSummary', data={'email': ''})
    assert response.status_code == 302
    
def test_showSummary_invalid_email(client):
    """
    Teste le comportement de showSummary lorsque l'email est invalide.
    """
    response = client.post('/showSummary', data={'email': 'email_invalide'})
    assert response.status_code == 302

def test_showSummary_unknow_email(client):
    """
    Teste le comportement de showSummary lorsque l'email est inconnu.
    """
    response = client.post('/showSummary', data={'email': 'email_inconnu@example.com'})
    assert response.status_code == 302