import requests

BASE = "http://127.0.0.1:5000"

def demo():
    print("GET /api/rfis")
    print(requests.get(f"{BASE}/api/rfis").json())

    payload = {
        "externalKey": "DEMO-001",
        "projectId": 1,
        "title": "Demo created via client",
        "createdAt": "2025-11-12",
        "status": "Open",
        "priority": "High"
    }
    print("POST /api/rfis")
    print(requests.post(f"{BASE}/api/rfis", json=payload).json())

    print("PUT /api/rfis/1 (status=Closed)")
    print(requests.put(f"{BASE}/api/rfis/1", json={"status":"Closed"}).json())

if __name__ == "__main__":
    demo()
