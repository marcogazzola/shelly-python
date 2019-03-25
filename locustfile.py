from locust import HttpLocust, TaskSet

def settings(l):
    l.client.post("/settings", {"username":"admin", "password":"admin"})

def status(l):
    l.client.post("/status", {"username":"admin", "password":"admin"})

class UserBehavior(TaskSet):
    tasks = {settings: 1, status: 1}

class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 5000
    max_wait = 9000