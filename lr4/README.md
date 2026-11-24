# ЛР4 DutyCloud: function calling, MCP, A2A
Потрібна запущена система DutyCloud з ЛР3 (gateway на http://localhost:8000).

Налаштування LLM (Gemini, OpenAI-сумісний ендпоінт), вводити в терміналі, НЕ в файли:
  export OPENAI_API_KEY=...
  export OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
  export MODEL=gemini-flash-latest

Запуск:
  pip install -r requirements.txt
  python fc_client.py --demo
  python mcp_server.py http       # + npx @modelcontextprotocol/inspector
  python a2a_consumer.py ; python a2a_producer.py ; python a2a_demo.py   (3 термінали)
