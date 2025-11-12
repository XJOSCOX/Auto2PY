from datetime import datetime, date
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from .db import get_conn, add_notification
from .reports import export_notifications_csv  # <-- add this import

def check_overdue():
    today = date.today().isoformat()
    created = 0
    with get_conn() as c:
        rows = c.execute("""SELECT id, title, externalKey, dueDate, status
                            FROM rfis
                            WHERE dueDate IS NOT NULL AND dueDate < ? AND status != 'Closed'""", (today,)).fetchall()
        for r in rows:
            msg = f"RFI {r['externalKey']} '{r['title']}' is OVERDUE (due {r['dueDate']})."
            add_notification(r["id"], "OVERDUE", msg, datetime.utcnow().isoformat()+"Z")
            created += 1

    # ⬇️ NEW: write/refresh notifications CSV after each run
    csv_path = export_notifications_csv()
    print(f"🔔 Overdue check: created {created} notifications | CSV: {csv_path}")

if __name__ == "__main__":
    sched = BlockingScheduler(timezone="UTC")
    # run once at start
    check_overdue()
    # run daily at 08:00 Central (CT ~ UTC-6 standard; naive UTC 14:00 here for demo)
    sched.add_job(check_overdue, CronTrigger(hour=14, minute=0))
    print("⏱️ Scheduler running (daily 08:00 CT)...")
    sched.start()
