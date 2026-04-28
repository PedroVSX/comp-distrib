from locust import HttpUser, between, task


class WordPressUser(HttpUser):
    wait_time = between(1, 3)

    @task(5)
    def index(self):
        self.client.get("")

    @task(1)
    def view_post(self):
        # try a common WP path
        self.client.get("/?p=1")
