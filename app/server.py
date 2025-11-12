from flask import Flask, request, jsonify
from .db import get_conn, upsert_rfi

app = Flask(__name__)

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

if __name__ == "__main__":
    app.run(debug=True)
