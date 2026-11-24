"""Завдання 3а. Producer (schedule-service) як AI-агент A2A, порт 9001.
Навички: produce_assignment (подія AssignmentCreated через outbox) і create_schedule.
Після продукування звертається до consumer-агента через A2A."""
import os

import fc_client
from a2a_common import fetch_card, make_app, make_card, send_message
from dutycloud_api import dc

URL = os.getenv("PRODUCER_URL", "http://localhost:9001")
CONSUMER = os.getenv("CONSUMER_URL", "http://localhost:9002")

SKILLS = [{
    "id": "produce_assignment",
    "name": "Продукування події призначення",
    "description": "Створює призначення (SAGA + Transactional Outbox, подія schedule.AssignmentCreated) "
                   "і просить consumer-агента підтвердити сповіщення.",
    "tags": ["producer", "outbox", "saga"],
    "examples": ["Призначи ivan на чергування 2026-11-10 з 10:00 до 12:00"],
}, {
    "id": "create_schedule",
    "name": "Створення розкладу",
    "description": "Створює чернетку розкладу (подія ScheduleCreated).",
    "tags": ["producer"],
}]


def handle(text, data):
    skill = data.get("skill")
    if skill == "create_schedule":
        return dc.create_schedule(data.get("title", "A2A schedule"))["body"]
    if skill == "produce_assignment":
        sid = data.get("schedule_id") or dc.create_schedule("A2A schedule")["body"]["id"]
        r = dc.create_assignment(sid, data["participant"], data["date"], data["start"], data["end"])
        if r["http"] != 202:
            raise RuntimeError(f"schedule-service: {r['http']} {r['body']}")
        res = r["body"]
        card = fetch_card(CONSUMER)  # A2A discovery
        state, out = send_message(CONSUMER, data={"skill": "confirm_notification",
                                                  "assignment_id": res["id"]})
        return {"producer": res, "consumer_agent": card["name"], "consumer_state": state, "consumer_result": out}
    # вільний текст: AI-агент сам вибирає інструменти (function calling з Завдання 1)
    return {"answer": fc_client.run(text)}


app = make_app(make_card("DutyCloud Producer Agent",
                         "Агент schedule-service: продукує події розкладу та призначень.", URL, SKILLS), handle)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9001)
