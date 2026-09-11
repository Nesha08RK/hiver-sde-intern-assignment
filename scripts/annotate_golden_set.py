"""Serve a small local UI for manually annotating a selected CSV file."""

from __future__ import annotations

import argparse
import csv
import json
import os
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "evaluation" / "golden_set_150.csv"

INTENTS = [
    "Delivery and order fulfillment",
    "Customer service escalation and feedback",
    "Product condition, item accuracy, and seller issues",
    "Digital products, devices, and apps",
    "Prime membership and benefits",
    "Returns, refunds, and charges",
    "Pricing, offers, and product availability",
    "Account access and security",
    "Other/Unclear/non-substantive",
]
ESCALATION_VALUES = {"AUTO_HANDLE", "ESCALATE"}
REVIEWER_FIELDS = {
    "reviewer_intent",
    "reviewer_expected_escalation",
    "reviewer_notes",
}


def reviewer_fields(fieldnames: list[str]) -> set[str]:
    if "reviewer_expected_escalation" in fieldnames:
        return REVIEWER_FIELDS
    return {"reviewer_intent", "reviewer_notes"}


def load_rows() -> tuple[list[str], list[dict[str, str]]]:
    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames:
            raise RuntimeError(f"CSV has no header: {CSV_PATH}")
        return reader.fieldnames, list(reader)


def save_reviewer_fields(index: int, values: dict[str, str]) -> dict[str, int]:
    fieldnames, rows = load_rows()
    allowed_fields = reviewer_fields(fieldnames)
    if index < 0 or index >= len(rows):
        raise ValueError("Example index is out of range")
    if set(values) != allowed_fields:
        raise ValueError("Unexpected reviewer fields submitted")
    if values["reviewer_intent"] not in INTENTS:
        raise ValueError("Invalid reviewer intent")
    if "reviewer_expected_escalation" in values and values["reviewer_expected_escalation"] not in ESCALATION_VALUES:
        raise ValueError("Invalid reviewer escalation value")

    rows[index].update(values)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        newline="",
        dir=CSV_PATH.parent,
        delete=False,
    ) as temporary:
        writer = csv.DictWriter(temporary, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        temporary_path = Path(temporary.name)
    os.replace(temporary_path, CSV_PATH)

    completed = sum(bool(row["reviewer_intent"].strip()) for row in rows)
    if "reviewer_expected_escalation" in fieldnames:
        completed = sum(
            bool(row["reviewer_intent"].strip())
            and bool(row["reviewer_expected_escalation"].strip())
            for row in rows
        )
    return {"completed": completed, "total": len(rows)}


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AmazonHelp Golden Set Annotation</title>
<style>
:root { color-scheme: light; font-family: Segoe UI, sans-serif; }
body { margin: 0; background: #f3f6f8; color: #17212b; }
main { max-width: 1100px; margin: 0 auto; padding: 24px; }
header, section { background: white; border: 1px solid #d7e0e7; border-radius: 8px; padding: 20px; margin-bottom: 16px; }
h1 { margin: 0 0 6px; font-size: 24px; }
.muted { color: #52616b; }
.progress { font-weight: 700; color: #075985; }
.label { display: block; margin: 14px 0 6px; font-weight: 700; }
.message, pre { white-space: pre-wrap; overflow-wrap: anywhere; background: #f7fafc; border: 1px solid #e1e8ee; border-radius: 6px; padding: 14px; line-height: 1.45; }
pre { max-height: 360px; overflow: auto; font: 14px/1.45 Consolas, monospace; }
select, textarea { width: 100%; box-sizing: border-box; border: 1px solid #aab8c2; border-radius: 5px; padding: 10px; font: inherit; background: white; }
textarea { min-height: 90px; resize: vertical; }
.actions { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }
button { border: 0; border-radius: 5px; padding: 10px 16px; font: inherit; font-weight: 700; cursor: pointer; }
button.primary { background: #075985; color: white; }
button.secondary { background: #e2e8f0; color: #17212b; }
button:disabled { opacity: .5; cursor: not-allowed; }
.status { min-height: 22px; color: #166534; font-weight: 600; }
.error { color: #b91c1c; }
.weak { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
@media (max-width: 700px) { main { padding: 12px; } .weak { grid-template-columns: 1fr; } }
</style>
</head>
<body>
<main>
<header>
  <h1>AmazonHelp Golden Set Annotation</h1>
  <div id="progress" class="progress">Loading...</div>
    <div class="muted">Manual decisions are saved to the selected CSV. Weak labels are reference suggestions only.</div>
</header>
<section>
  <div class="label">Customer message</div>
  <div id="message" class="message"></div>
  <div class="label">Conversation context</div>
  <pre id="context"></pre>
  <div class="weak">
    <div><span class="label">Existing weak intent</span><div id="weakIntent" class="message"></div></div>
    <div><span class="label">Existing weak escalation</span><div id="weakEscalation" class="message"></div></div>
  </div>
</section>
<section>
  <label class="label" for="intent">Reviewer intent</label>
  <select id="intent"><option value="">Select an intent...</option></select>
    <div id="escalationFields">
        <label class="label" for="escalation">Escalate? (Yes = ESCALATE, No = AUTO_HANDLE)</label>
        <select id="escalation">
            <option value="">Select Yes or No...</option>
            <option value="ESCALATE">Yes</option>
            <option value="AUTO_HANDLE">No</option>
        </select>
    </div>
  <label class="label" for="notes">Reviewer notes (optional)</label>
  <textarea id="notes" placeholder="Add reasoning for ambiguous or escalation-heavy cases..."></textarea>
  <div id="status" class="status"></div>
  <div class="actions">
    <button id="previous" class="secondary">Previous</button>
    <button id="save" class="primary">Save</button>
    <button id="next" class="primary">Save and Next</button>
  </div>
</section>
</main>
<script>
let examples = [];
let hasEscalation = true;
let index = Number(localStorage.getItem('amazonhelp-annotation-index') || 0);
const intent = document.getElementById('intent');
const escalation = document.getElementById('escalation');
const notes = document.getElementById('notes');
const status = document.getElementById('status');

function setStatus(text, error = false) {
  status.textContent = text;
  status.className = error ? 'status error' : 'status';
}

function render() {
  const item = examples[index];
  document.getElementById('progress').textContent = `Example ${index + 1} of ${examples.length} | ${item.example_id}`;
  document.getElementById('message').textContent = item.customer_message;
  document.getElementById('context').textContent = item.context;
    document.getElementById('weakIntent').textContent = item.weak_intent || item.intent || '(empty)';
  document.getElementById('weakEscalation').textContent = item.expected_escalation || '(empty)';
  intent.value = item.reviewer_intent || '';
  escalation.value = item.reviewer_expected_escalation || '';
  notes.value = item.reviewer_notes || '';
  document.getElementById('previous').disabled = index === 0;
  document.getElementById('next').textContent = index === examples.length - 1 ? 'Save' : 'Save and Next';
  localStorage.setItem('amazonhelp-annotation-index', String(index));
  setStatus('');
}

async function save() {
    if (!intent.value || (hasEscalation && !escalation.value)) {
    setStatus('Select both a reviewer intent and an escalation answer before saving.', true);
    return false;
  }
    const payload = {index, reviewer_intent: intent.value, reviewer_notes: notes.value};
    if (hasEscalation) payload.reviewer_expected_escalation = escalation.value;
    const response = await fetch('/api/save', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(payload)
  });
  const result = await response.json();
  if (!response.ok) { setStatus(result.error || 'Save failed.', true); return false; }
    Object.assign(examples[index], payload);
  setStatus(`Saved. ${result.completed} of ${result.total} examples completed.`);
  return true;
}

document.getElementById('save').onclick = save;
document.getElementById('next').onclick = async () => { if (await save() && index < examples.length - 1) { index++; render(); } };
document.getElementById('previous').onclick = async () => { if (index > 0) { index--; render(); } };

fetch('/api/examples').then(response => response.json()).then(data => {
  examples = data.examples;
    hasEscalation = data.has_escalation;
    document.getElementById('escalationFields').style.display = hasEscalation ? '' : 'none';
  if (!examples.length) throw new Error('No examples found.');
  index = Math.min(Math.max(index, 0), examples.length - 1);
  const options = data.intents.map(value => `<option value="${value.replaceAll('"', '&quot;')}">${value}</option>`).join('');
  intent.insertAdjacentHTML('beforeend', options);
  render();
}).catch(error => setStatus(error.message, true));
</script>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    def send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/":
            body = PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if path == "/api/examples":
            fieldnames, rows = load_rows()
            self.send_json({
                "examples": rows,
                "intents": INTENTS,
                "has_escalation": "reviewer_expected_escalation" in fieldnames,
            })
            return
        self.send_error(404)

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/save":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length))
            index = int(payload["index"])
            fieldnames, _ = load_rows()
            fields = reviewer_fields(fieldnames)
            values = {field: str(payload[field]) for field in fields}
            summary = save_reviewer_fields(index, values)
            self.send_json(summary)
        except (KeyError, TypeError, ValueError, json.JSONDecodeError, RuntimeError) as error:
            self.send_json({"error": str(error)}, 400)

    def log_message(self, format: str, *args: object) -> None:
        print(f"{self.address_string()} - {format % args}")


def main() -> None:
    global CSV_PATH
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=CSV_PATH)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    CSV_PATH = args.csv if args.csv.is_absolute() else ROOT / args.csv
    if not CSV_PATH.exists():
        raise SystemExit(f"Annotation file not found: {CSV_PATH}")
    print(f"Annotating: {CSV_PATH}")
    print(f"Open http://{args.host}:{args.port}/ in your browser")
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nAnnotation server stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()