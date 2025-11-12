import csv
from pathlib import Path
from .db import get_conn

OUT_DIR = Path(__file__).resolve().parent.parent / "out"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def export_notifications_csv() -> str:
    """Dump all notifications (with useful RFI context) to out/notifications.csv."""
    with get_conn() as c:
        rows = c.execute(
            """SELECT
                 n.id          AS notificationId,
                 n.type        AS type,
                 n.message     AS message,
                 n.createdAt   AS createdAt,
                 r.externalKey AS rfiExternalKey,
                 r.title       AS rfiTitle,
                 r.status      AS rfiStatus,
                 r.dueDate     AS rfiDueDate,
                 p.code        AS projectCode,
                 p.name        AS projectName
               FROM notifications n
               JOIN rfis r     ON r.id = n.rfiId
               JOIN projects p ON p.id = r.projectId
               ORDER BY n.createdAt DESC"""
        ).fetchall()

    path = OUT_DIR / "notifications.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "notificationId","type","message","createdAt",
            "rfiExternalKey","rfiTitle","rfiStatus","rfiDueDate",
            "projectCode","projectName"
        ])
        for r in rows:
            w.writerow([
                r["notificationId"], r["type"], r["message"], r["createdAt"],
                r["rfiExternalKey"], r["rfiTitle"], r["rfiStatus"], r["rfiDueDate"],
                r["projectCode"], r["projectName"],
            ])
    return str(path)

def export_rfis_csv() -> str:
    """Optional: dump all RFIs to out/rfis.csv for reporting."""
    with get_conn() as c:
        rows = c.execute(
            """SELECT
                 r.id, r.externalKey, r.title, r.status, r.priority,
                 r.createdAt, r.dueDate, r.closedAt, r.assignee,
                 p.code AS projectCode, p.name AS projectName
               FROM rfis r
               JOIN projects p ON p.id = r.projectId
               ORDER BY r.createdAt DESC"""
        ).fetchall()

    path = OUT_DIR / "rfis.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "id","externalKey","title","status","priority",
            "createdAt","dueDate","closedAt","assignee",
            "projectCode","projectName"
        ])
        for r in rows:
            w.writerow([
                r["id"], r["externalKey"], r["title"], r["status"], r["priority"],
                r["createdAt"], r["dueDate"], r["closedAt"], r["assignee"],
                r["projectCode"], r["projectName"]
            ])
    return str(path)
