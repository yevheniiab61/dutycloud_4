"""REST-клієнт DutyCloud (через Traefik gateway з ЛР3). Шляхи й поля взято з demo.py та app.py ЛР3."""
import os
import requests

BASE = os.getenv("DUTYCLOUD_URL", "http://localhost:8000")
USER = os.getenv("DC_USER", "admin")
PASSWORD = os.getenv("DC_PASS", "admin")


class DutyCloud:
    def __init__(self):
        self.s = requests.Session()
        self.logged = False

    def login(self):
        r = self.s.post(f"{BASE}/api/identity/login", json={"username": USER, "password": PASSWORD}, timeout=10)
        r.raise_for_status()
        self.s.headers["Authorization"] = "Bearer " + r.json()["token"]
        self.logged = True

    def call(self, method, path, **kw):
        if not self.logged:
            self.login()
        r = self.s.request(method, BASE + path, timeout=10, **kw)
        try:
            body = r.json()
        except ValueError:
            body = r.text
        return {"http": r.status_code, "body": body}

    # --- schedule-service ---
    def create_schedule(self, title):
        return self.call("POST", "/api/schedule/schedules", json={"title": title})

    def create_assignment(self, schedule_id, participant, date, start, end):
        return self.call("POST", f"/api/schedule/schedules/{schedule_id}/assignments",
                         json={"participant": participant, "date": date, "start": start, "end": end})

    def get_assignment(self, aid):
        return self.call("GET", f"/api/schedule/assignments/{aid}")

    def update_assignment(self, aid, **fields):
        return self.call("PUT", f"/api/schedule/assignments/{aid}", json=fields)

    def publish_schedule(self, sid):
        return self.call("POST", f"/api/schedule/schedules/{sid}/publish")

    def sagas(self):
        return self.call("GET", "/api/schedule/sagas")

    # --- notification-service ---
    def inbox(self):
        return self.call("GET", "/api/notifications/inbox")


dc = DutyCloud()
