import argparse, json
from pathlib import Path
from datetime import date
from dateutil import parser as dtp
from .db import upsert_project, upsert_vendor, upsert_rfi

def coerce_date(val):
    if not val: return None
    if isinstance(val, (date,)): return val.isoformat()
    return dtp.parse(str(val)).date().isoformat()

def validate_rfi(obj: dict):
    required = ["externalKey","projectCode","projectName","title","createdAt"]
    for k in required:
        if k not in obj or obj[k] in (None, ""):
            raise ValueError(f"Missing required field: {k}")

def ingest_dir(path: Path):
    count = 0
    for p in sorted(Path(path).glob("*.json")):
        obj = json.loads(p.read_text(encoding="utf-8"))
        validate_rfi(obj)

        project_id = upsert_project(obj["projectCode"], obj["projectName"])
        vendor_id = upsert_vendor(obj.get("vendorName"), obj.get("vendorEmail"))

        payload = {
            "externalKey": obj["externalKey"],
            "projectId": project_id,
            "vendorId": vendor_id,
            "title": obj["title"],
            "status": obj.get("status","Open"),
            "createdAt": coerce_date(obj["createdAt"]),
            "dueDate": coerce_date(obj.get("dueDate")),
            "closedAt": coerce_date(obj.get("closedAt")),
            "priority": obj.get("priority","Normal"),
            "assignee": obj.get("assignee")
        }
        upsert_rfi(payload)
        count += 1
    print(f"✅ Ingested {count} RFIs from {path}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", required=True, help="Folder with *.json RFIs")
    args = ap.parse_args()
    ingest_dir(Path(args.path))
