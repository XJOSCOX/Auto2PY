from flask import Flask, request, jsonify, send_from_directory
from pathlib import Path
from .db import get_conn, upsert_rfi

app = Flask(__name__)

# --- CORS for local dev ---
@app.after_request
def add_cors_headers(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, OPTIONS"
    return resp

@app.route("/api/rfis", methods=["OPTIONS"])
@app.route("/api/rfis/<int:_rid>", methods=["OPTIONS"])
def cors_preflight(_rid=None):
    return ("", 204)

# --- REST endpoints ---
@app.get("/api/rfis")
def list_rfis():
    with get_conn() as c:
        rows = c.execute("""SELECT r.*, p.code as projectCode, p.name as projectName, v.name as vendorName
                            FROM rfis r
                            JOIN projects p ON p.id = r.projectId
                            LEFT JOIN vendors v ON v.id = r.vendorId
                            ORDER BY r.createdAt DESC""").fetchall()
        return jsonify([dict(r) for r in rows])

@app.post("/api/rfis")
def create_rfi():
    payload = request.json or {}
    required = ["externalKey","projectId","title","createdAt"]
    for k in required:
        if k not in payload:
            return {"error": f"Missing {k}"}, 400
    rid = upsert_rfi(payload)
    return {"id": rid}, 201

@app.put("/api/rfis/<int:rid>")
def update_rfi(rid: int):
    payload = request.json or {}
    sets, vals = [], []
    allowed = ["status","dueDate","closedAt","priority","assignee","title","vendorId","projectId"]
    for k in allowed:
        if k in payload:
            sets.append(f"{k}=?")
            vals.append(payload[k])
    if not sets:
        return {"error":"No updatable fields"}, 400
    vals.append(rid)
    with get_conn() as c:
        c.execute(f"UPDATE rfis SET {', '.join(sets)} WHERE id=?", vals)
    return {"ok": True}

@app.get("/api/notifications")
def list_notifications():
    with get_conn() as c:
        rows = c.execute("""SELECT n.*, r.title, r.externalKey
                            FROM notifications n
                            JOIN rfis r ON r.id = n.rfiId
                            ORDER BY n.createdAt DESC""").fetchall()
        return jsonify([dict(r) for r in rows])

# --- serve CSVs from out/ for convenience ---
OUT_DIR = Path(__file__).resolve().parent.parent / "out"
OUT_DIR.mkdir(parents=True, exist_ok=True)

@app.get("/files/<path:filename>")
def files(filename: str):
    return send_from_directory(OUT_DIR, filename, as_attachment=False)

if __name__ == "__main__":
    app.run(debug=True)
