"""Мінімальна реалізація A2A (JSON-RPC 2.0 over HTTP): Agent Card, message/send, tasks/get."""
import uuid

import requests
from flask import Flask, jsonify, request


def make_app(card, handle):
    app, tasks = Flask(__name__), {}

    @app.get("/.well-known/agent-card.json")
    @app.get("/.well-known/agent.json")
    def agent_card():
        return jsonify(card)

    @app.post("/")
    def rpc():
        req = request.get_json(force=True)
        rid, method = req.get("id"), req.get("method")
        if method == "message/send":
            msg = req["params"]["message"]
            text = " ".join(p.get("text", "") for p in msg["parts"] if p.get("kind") == "text")
            data = next((p["data"] for p in msg["parts"] if p.get("kind") == "data"), {})
            try:
                result, state = handle(text, data), "completed"
            except Exception as e:  # noqa: BLE001
                result, state = {"error": str(e)}, "failed"
            task = {"kind": "task", "id": str(uuid.uuid4()),
                    "contextId": msg.get("contextId") or str(uuid.uuid4()),
                    "status": {"state": state},
                    "artifacts": [{"artifactId": str(uuid.uuid4()), "name": "result",
                                   "parts": [{"kind": "data", "data": result}]}]}
            tasks[task["id"]] = task
            return jsonify({"jsonrpc": "2.0", "id": rid, "result": task})
        if method == "tasks/get":
            t = tasks.get(req["params"]["id"])
            if t:
                return jsonify({"jsonrpc": "2.0", "id": rid, "result": t})
            return jsonify({"jsonrpc": "2.0", "id": rid, "error": {"code": -32001, "message": "Task not found"}})
        return jsonify({"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": "Method not found"}})

    return app


def make_card(name, desc, url, skills):
    return {"protocolVersion": "0.3.0", "name": name, "description": desc, "url": url,
            "version": "1.0.0", "capabilities": {"streaming": False},
            "defaultInputModes": ["text/plain", "application/json"],
            "defaultOutputModes": ["application/json"], "skills": skills}


def fetch_card(url):
    return requests.get(url + "/.well-known/agent-card.json", timeout=10).json()


def send_message(url, text=None, data=None):
    parts = ([{"kind": "text", "text": text}] if text else []) + ([{"kind": "data", "data": data}] if data else [])
    body = {"jsonrpc": "2.0", "id": str(uuid.uuid4()), "method": "message/send",
            "params": {"message": {"kind": "message", "role": "user",
                                   "messageId": str(uuid.uuid4()), "parts": parts}}}
    r = requests.post(url, json=body, timeout=60).json()
    if "error" in r:
        raise RuntimeError(r["error"]["message"])
    task = r["result"]
    return task["status"]["state"], task["artifacts"][0]["parts"][0]["data"]
