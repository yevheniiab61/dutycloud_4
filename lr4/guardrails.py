"""Спільні guardrails для function-calling клієнта та MCP-сервера."""
import json
import re
import time
import uuid as _uuid
from datetime import datetime

NAME_RE = re.compile(r"^[a-z0-9._-]{2,32}$")
INJECTION_RE = re.compile(
    r"(ignore|disregard|forget)\s+(all\s+|any\s+|the\s+|your\s+)*(previous|prior|above)?\s*(instructions|rules|prompt)"
    r"|system\s+prompt|you\s+are\s+now|"
    r"(ігноруй|забудь|знехтуй)\s+(усі\s+|всі\s+|попередні\s+)*(інструкції|правила|промпт)"
    r"|нові\s+інструкції|<\s*/?\s*(system|tool_result|assistant)",
    re.I,
)
MAX_OUT_CHARS = 1500


def v_name(x):
    if not isinstance(x, str) or not NAME_RE.match(x):
        raise ValueError("participant: очікується [a-z0-9._-], 2-32 символи")
    return x


def v_uuid(x):
    try:
        return str(_uuid.UUID(str(x)))
    except ValueError:
        raise ValueError("id має бути UUID")


def v_date(x):
    try:
        datetime.strptime(x, "%Y-%m-%d")
    except (TypeError, ValueError):
        raise ValueError("date має бути у форматі YYYY-MM-DD")
    return x


def v_time(x):
    try:
        datetime.strptime(x, "%H:%M")
    except (TypeError, ValueError):
        raise ValueError("час має бути у форматі HH:MM")
    return x


def sanitize(text):
    """Вирізає типові фрази prompt injection з недовірених даних."""
    cleaned, n = INJECTION_RE.subn("[ЗАБЛОКОВАНО: ймовірна prompt injection]", text)
    return cleaned, n > 0


def safe_output(obj, limit=MAX_OUT_CHARS):
    s = json.dumps(obj, ensure_ascii=False, default=str)
    s, flagged = sanitize(s)
    if flagged:
        print("[guardrail] виявлено ймовірну prompt injection у відповіді API")
    if len(s) > limit:
        s = s[:limit] + "...[обрізано]"
    return s


class RateLimiter:
    def __init__(self, n=30, per=60):
        self.n, self.per, self.calls = n, per, []

    def check(self):
        now = time.time()
        self.calls = [t for t in self.calls if now - t < self.per]
        if len(self.calls) >= self.n:
            raise RuntimeError("rate limit: забагато викликів, спробуйте пізніше")
        self.calls.append(now)


limiter = RateLimiter()
