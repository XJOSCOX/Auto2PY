# RFI Sync Demo (New Automation Project)

This is a Procore-style automation to demonstrate:
- Python REST API (Flask)
- SQLite with upserts
- APScheduler automation for overdue RFIs
- JSON ingestion
- REST client demo

### How to run

```bash
pip install -r requirements.txt
python -m app.db --init
python -m app.ingest --path data/rfi
python -m app.server
python -m app.scheduler
python -m app.client_demo
