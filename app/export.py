from .reports import export_notifications_csv, export_rfis_csv

if __name__ == "__main__":
    n = export_notifications_csv()
    r = export_rfis_csv()
    print(f"✅ Wrote:\n  - {n}\n  - {r}")
