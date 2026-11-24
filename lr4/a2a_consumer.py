"""Завдання 3б. Consumer (notification-service) як A2A-агент, порт 9002."""
import json
import os
import time

from a2a_common import make_app, make_card
from dutycloud_api import dc

URL = os.getenv("CONSUMER_URL", "http://localhost:9002")

SKILLS = [{
    "id": "confirm_notification",
    "name": "Підтвердження сповіщення",
    "description": "Чекає, поки consumer обробить подію AssignmentCreated, і повертає результат саги "
                   "(ACTIVE = сповіщення записано, CANCELLED = відкат через DLQ або TIMEOUT).",
    "tags": ["notification", "saga"],
    "examples": ["Підтверди сповіщення для призначення <uuid>"],
}, {
    "id": "list_inbox",
    "name": "Inbox консьюмера",
    "description": "Повертає записи inbox notification-service (done / failed).",
    "tags": ["inbox"],
}]


def handle(text, data):
    skill = data.get("skill") or ("list_inbox" if "inbox" in text.lower() else "confirm_notification")
    if skill == "list_inbox":
        return {"inbox": dc.inbox()["body"]}
    aid = data["assignment_id"]
    deadline = time.time() + float(data.get("wait_sec", 30))
    while time.time() < deadline:
        a = dc.get_assignment(aid)["body"]
        if isinstance(a, dict) and a.get("status") != "PENDING":
            return {"assignment_id": aid, "status": a.get("status"),
                    "notified": a.get("status") == "ACTIVE"}
        time.sleep(1)
    return {"assignment_id": aid, "status": "PENDING", "notified": False, "note": "wait timeout"}


app = make_app(make_card("DutyCloud Consumer Agent",
                         "Агент notification-service: підтверджує обробку подій і сповіщення.", URL, SKILLS), handle)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9002)
