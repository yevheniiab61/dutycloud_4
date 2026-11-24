"""Інструменти поверх REST API DutyCloud (спільні для function calling і MCP)."""
from dutycloud_api import dc
from guardrails import limiter, safe_output, v_date, v_name, v_time, v_uuid


def find_assignments(participant: str | None = None):
    """Активні (PENDING/ACTIVE) призначення з журналу саг, за потреби лише учасника."""
    limiter.check()
    body = dc.sagas()["body"]
    items = body.get("items", []) if isinstance(body, dict) else []
    if participant:
        v_name(participant)
        items = [i for i in items if i.get("participant") == participant]
    items = [{"assignment_id": i["assignment_id"], "participant": i["participant"],
              "status": i["assignment_status"], "saga": i["state"]}
             for i in items if i.get("assignment_status") in ("PENDING", "ACTIVE")]
    return safe_output(items[:15])


def get_assignment(assignment_id: str):
    limiter.check()
    return safe_output(dc.get_assignment(v_uuid(assignment_id)))


def create_schedule(title: str):
    limiter.check()
    if not isinstance(title, str) or not 1 <= len(title) <= 100:
        raise ValueError("title: 1-100 символів")
    return safe_output(dc.create_schedule(title))


def create_assignment(schedule_id: str, participant: str, date: str, start: str, end: str):
    limiter.check()
    if v_time(start) >= v_time(end):
        raise ValueError("start має бути раніше за end")
    return safe_output(dc.create_assignment(v_uuid(schedule_id), v_name(participant), v_date(date), start, end))


def update_assignment(assignment_id: str, date: str | None = None, start: str | None = None,
                      end: str | None = None):
    limiter.check()
    fields = {}
    if date:
        fields["date"] = v_date(date)
    if start:
        fields["start"] = v_time(start)
    if end:
        fields["end"] = v_time(end)
    if not fields:
        raise ValueError("потрібно вказати date, start і/або end")
    return safe_output(dc.update_assignment(v_uuid(assignment_id), **fields))


def publish_schedule(schedule_id: str):
    limiter.check()
    return safe_output(dc.publish_schedule(v_uuid(schedule_id)))


def get_sagas():
    limiter.check()
    body = dc.sagas()["body"]
    items = body.get("items", [])[:10] if isinstance(body, dict) else body
    return safe_output(items)


IMPL = {f.__name__: f for f in (find_assignments, get_assignment, create_schedule, create_assignment,
                                update_assignment, publish_schedule, get_sagas)}
