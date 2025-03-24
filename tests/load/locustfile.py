from locust import HttpUser, task, between


class ShortUrlUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def create_short_link(self):
        self.client.post("/links/shorten",
                         json={"original_url": "https://example.com"})

    @task
    def access_short_link(self):
        self.client.get("/links/test_code")

    @task
    def get_stats(self):
        self.client.get("/links/test_code/stats")
