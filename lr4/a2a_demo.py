"""Демо A2A: Agent Cards обох агентів + виклик навички producer (він викликає consumer)."""
import json
import random
from datetime import datetime, timedelta

from a2a_common import fetch_card, send_message
from dutycloud_api import dc

PRODUCER, CONSUMER = "http://localhost:9001", "http://localhost:9002"
show = lambda x: print(json.dumps(x, ensure_ascii=False, indent=2))  # noqa: E731

print("== Agent Cards =="); show(fetch_card(PRODUCER)); show(fetch_card(CONSUMER))
sid = dc.create_schedule("A2A demo")["body"]["id"]
day = lambda: (datetime.now() + timedelta(days=random.randint(30, 300))).strftime("%Y-%m-%d")  # noqa: E731
D = day()
print("== produce_assignment (успіх) ==")
show(send_message(PRODUCER, data={"skill": "produce_assignment", "schedule_id": sid,
                                  "participant": "ivan", "date": D, "start": "10:00", "end": "12:00"}))
print("== produce_assignment (fail-user -> DLQ -> CANCELLED) ==")
show(send_message(PRODUCER, data={"skill": "produce_assignment", "schedule_id": sid,
                                  "participant": "fail-user", "date": D, "start": "13:00", "end": "14:00"}))
print("== вільний текст (LLM вибирає інструменти) ==")
show(send_message(PRODUCER, text="Призначи petro на "+day()+" з 09:00 до 11:00 (створи для цього новий розклад)"))
