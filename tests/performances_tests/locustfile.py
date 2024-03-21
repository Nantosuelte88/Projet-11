from locust import HttpUser, task, between
from server import app


class ProjectPerfTest(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def index(self):
        self.client.get("/")

    @task(2)
    def display_board(self):
        self.client.get("/table")

    @task(3)
    def show_summary(self):
        response = self.client.post("/showSummary", data={'email': 'john@simplylift.co'})

    @task(2)
    def book(self):
        response = self.client.get("/book/Spring Festival/Simply Lift")

    @task(2)
    def purchase_places(self):
        response = self.client.post("/purchasePlaces", data={
            'competition': 'Spring Festival',
            'club': 'Simply Lift',
            'places': '2'
        })

    @task(1)
    def logout(self):
        self.client.get("/logout")