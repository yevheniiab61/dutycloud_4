"""Діагностика LLM: простий запит і запит з інструментами, із вимірюванням часу."""
import time
import fc_client as f

for name, kw in (("без інструментів", {}), ("з інструментами", {"tools": f.TOOLS})):
    t = time.time()
    try:
        r = f.client.chat.completions.create(
            model=f.MODEL, max_tokens=1024,
            messages=[{"role": "user", "content": "Покажи всі активні призначення"}], **kw)
        m = r.choices[0].message
        print(f"{name}: OK за {time.time()-t:.1f} с, tool_calls={[c.function.name for c in (m.tool_calls or [])]}, text={m.content!r}")
    except Exception as e:  # noqa: BLE001
        print(f"{name}: ПОМИЛКА за {time.time()-t:.1f} с: {type(e).__name__}: {str(e)[:400]}")
