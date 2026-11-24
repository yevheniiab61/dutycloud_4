"""Завдання 2. MCP-сервер для REST API DutyCloud (tools, resources, prompts + guardrails).
stdio:            python mcp_server.py
Streamable HTTP:  python mcp_server.py http     (http://localhost:8765/mcp)
Inspector:        npx @modelcontextprotocol/inspector python mcp_server.py"""
import sys

from mcp.server.fastmcp import FastMCP

import tools
from dutycloud_api import dc
from guardrails import safe_output, v_uuid

mcp = FastMCP("dutycloud", host="0.0.0.0", port=8765)


# ---------- Tools ----------
@mcp.tool()
def find_assignments(participant: str | None = None) -> str:
    """Активні призначення (PENDING/ACTIVE); participant – необов'язковий фільтр (a-z, 0-9, . _ -)."""
    return tools.find_assignments(participant)


@mcp.tool()
def get_assignment(assignment_id: str) -> str:
    """Деталі призначення (дата, час, статус) за UUID."""
    return tools.get_assignment(assignment_id)


@mcp.tool()
def create_schedule(title: str) -> str:
    """Створити розклад (чернетку); повертає id."""
    return tools.create_schedule(title)


@mcp.tool()
def create_assignment(schedule_id: str, participant: str, date: str, start: str, end: str) -> str:
    """Створити призначення (SAGA: спершу PENDING, потім ACTIVE або CANCELLED). date YYYY-MM-DD, час HH:MM."""
    return tools.create_assignment(schedule_id, participant, date, start, end)


@mcp.tool()
def update_assignment(assignment_id: str, date: str | None = None, start: str | None = None,
                      end: str | None = None) -> str:
    """Змінити дату/час призначення за id."""
    return tools.update_assignment(assignment_id, date, start, end)


@mcp.tool()
def publish_schedule(schedule_id: str, confirm: bool = False) -> str:
    """Опублікувати розклад (подія SchedulePublished). Незворотна дія: працює лише з confirm=true."""
    if not confirm:
        return "Відхилено: для публікації передайте confirm=true після підтвердження користувачем."
    return tools.publish_schedule(schedule_id)


# ---------- Resources ----------
@mcp.resource("dutycloud://sagas")
def sagas() -> str:
    """Журнал саг schedule-service."""
    return tools.get_sagas()


@mcp.resource("dutycloud://assignments/{assignment_id}")
def assignment(assignment_id: str) -> str:
    """Одне призначення за id."""
    return safe_output(dc.get_assignment(v_uuid(assignment_id)))


# ---------- Prompts ----------
@mcp.prompt()
def assign_duty(participant: str, date: str, start_time: str, end_time: str) -> str:
    """Шаблон: призначити або оновити чергування учасника."""
    return (f"Для учасника {participant} на {date} з {start_time} до {end_time}: знайди його призначення "
            "через find_assignments; якщо є – онови час, якщо немає – створи розклад і призначення. "
            "Нічого не публікуй без підтвердження.")


if __name__ == "__main__":
    mcp.run(transport="streamable-http" if "http" in sys.argv else "stdio")
