import argparse, sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "rfi.sqlite3"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    with get_conn() as c:
        c.executescript(sql)

def upsert_project(code: str, name: str) -> int:
    with get_conn() as c:
        row = c.execute("SELECT id FROM projects WHERE code=?", (code,)).fetchone()
        if row: return row["id"]
        c.execute("INSERT INTO projects(code, name) VALUES(?,?)", (code, name))
        return c.execute("SELECT id FROM projects WHERE code=?", (code,)).fetchone()["id"]

def upsert_vendor(name: str, email: str|None) -> int|None:
    if not name: return None
    with get_conn() as c:
        row = c.execute("SELECT id FROM vendors WHERE name=?", (name,)).fetchone()
        if row: return row["id"]
        c.execute("INSERT INTO vendors(name, email) VALUES(?,?)", (name, email))
        return c.execute("SELECT id FROM vendors WHERE name=?", (name,)).fetchone()["id"]

def upsert_rfi(payload: dict) -> int:
    with get_conn() as c:
        row = c.execute("SELECT id FROM rfis WHERE externalKey=?", (payload["externalKey"],)).fetchone()
        if row:
            c.execute(
                """UPDATE rfis SET projectId=?, vendorId=?, title=?, status=?, createdAt=?, dueDate=?, closedAt=?, priority=?, assignee=? 
                   WHERE externalKey=?""",
                (payload["projectId"], payload.get("vendorId"), payload["title"], payload.get("status","Open"),
                 payload["createdAt"], payload.get("dueDate"), payload.get("closedAt"),
                 payload.get("priority"), payload.get("assignee"), payload["externalKey"])
            )
            return row["id"]
        else:
            c.execute(
                """INSERT INTO rfis(externalKey, projectId, vendorId, title, status, createdAt, dueDate, closedAt, priority, assignee)
                   VALUES(?,?,?,?,?,?,?,?,?,?)""",
                (payload["externalKey"], payload["projectId"], payload.get("vendorId"), payload["title"],
                 payload.get("status","Open"), payload["createdAt"], payload.get("dueDate"),
                 payload.get("closedAt"), payload.get("priority"), payload.get("assignee"))
            )
            return c.execute("SELECT id FROM rfis WHERE externalKey=?", (payload["externalKey"],)).fetchone()["id"]

def add_notification(rfi_id: int, type_: str, message: str, createdAt: str):
    with get_conn() as c:
        c.execute("INSERT INTO notifications(rfiId, type, message, createdAt) VALUES(?,?,?,?)",
                  (rfi_id, type_, message, createdAt))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--init", action="store_true")
    args = parser.parse_args()
    if args.init:
        init_db()
        print("✅ DB initialized at", DB_PATH)
