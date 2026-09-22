"""Run synthetic main flows against running Vite + FastAPI + PostgreSQL.

Usage: DEMO_PASSWORD=... ../.venv/bin/python tests/e2e_http.py
"""

import os
import uuid

import httpx


BASE = os.getenv("E2E_BASE_URL", "http://127.0.0.1:5173")
PASSWORD = os.environ["DEMO_PASSWORD"]
suffix = uuid.uuid4().hex[:8]


def login(name):
    client = httpx.Client(base_url=BASE, timeout=10)
    response = client.post("/api/auth/login", json={"username": name, "password": PASSWORD})
    assert response.status_code == 200, (name, response.status_code, response.text)
    return client, {"X-CSRF-Token": response.json()["csrf_token"]}


member, member_headers = login("SunlitKoi")
volunteer, volunteer_headers = login("BrightKite")
moderator, moderator_headers = login("HSSModerator")

assert member.get("/api/auth/session").json()["user"]["username"] == "SunlitKoi"
assert member.get("/api/groups").json()
assert member.get("/api/content").json()

post = member.post("/api/content", json={"title": f"Synthetic school question {suffix}", "body": "This is a synthetic question for testing the community flow.", "format": "Question", "topic": "School and childcare", "stage": "Primary school"}, headers=member_headers)
assert post.status_code == 201, post.text
post_id = post.json()["id"]
assert member.put(f"/api/content/{post_id}/save", headers=member_headers).status_code == 204
assert member.put(f"/api/content/{post_id}/reaction", headers=member_headers).status_code == 204
assert member.get(f"/api/content/{post_id}").json()["saved"]
comment = member.post(f"/api/content/{post_id}/comments", json={"body": "Synthetic comment for the test."}, headers=member_headers)
assert comment.status_code == 201, comment.text
assert member.post(f"/api/content/{post_id}/comments", json={"body": "Synthetic reply for the test.", "parent_id": comment.json()["id"]}, headers=member_headers).status_code == 201
assert len(member.get(f"/api/content/{post_id}/comments").json()) == 2
assert any(x["id"] == post_id for x in member.get("/api/content").json())
assert any(x["content_id"] == post_id for x in member.get("/api/me/comments").json())
assert volunteer.delete(f"/api/content/{post_id}", headers=volunteer_headers).status_code == 403
assert member.post("/api/content", json={"title": "Call me on 8123 4567", "body": "This text has a synthetic contact detail.", "format": "Question", "topic": "Travel", "stage": "Primary school"}, headers=member_headers).status_code == 422

event_id = member.get("/api/events").json()[0]["id"]
assert member.put(f"/api/events/{event_id}/registration", headers=member_headers).status_code == 204
assert member.get("/api/events").json()[0]["registered"]
assert member.delete(f"/api/events/{event_id}/registration", headers=member_headers).status_code == 204

activity = member.post("/api/activities", json={"title": f"Synthetic walk {suffix}", "description": "A synthetic community meetup for the integration check.", "kind": "Meetup", "starts_at": "2099-10-10T10:00:00Z", "location": "Near Bedok MRT"}, headers=member_headers)
assert activity.status_code == 201, activity.text
activity_id = activity.json()["id"]
assert volunteer.put(f"/api/activities/{activity_id}/join", headers=volunteer_headers).status_code == 204
assert any(x["id"] == activity_id and x["joined"] for x in volunteer.get("/api/activities").json())
assert volunteer.delete(f"/api/activities/{activity_id}/join", headers=volunteer_headers).status_code == 204

help_request = member.post("/api/help-requests", json={"title": f"Synthetic errand {suffix}", "description": "A synthetic non-medical errand for the integration check.", "area": "Bedok", "non_medical_acknowledged": True}, headers=member_headers)
assert help_request.status_code == 201, help_request.text
help_id = help_request.json()["id"]
offer = volunteer.post(f"/api/help-requests/{help_id}/offers", headers=volunteer_headers)
assert offer.status_code == 201, offer.text
assert volunteer.get(f"/api/help-requests/{help_id}").json()["offers"] == []
assert member.get(f"/api/help-requests/{help_id}").json()["offers"][0]["volunteer"] == "BrightKite"
assert member.post(f"/api/help-requests/{help_id}/offers/{offer.json()['id']}/accept", headers=member_headers).status_code == 204
assert member.get(f"/api/help-requests/{help_id}").json()["status"] == "connected"

report = member.post("/api/reports", json={"target_type": "content", "target_id": post_id, "reason": "privacy", "details": "Synthetic review report."}, headers=member_headers)
assert report.status_code == 201, report.text
assert member.get("/api/reports").status_code == 403
assert any(x["id"] == report.json()["id"] for x in moderator.get("/api/reports").json())
assert moderator.patch(f"/api/reports/{report.json()['id']}", json={"status": "reviewed"}, headers=moderator_headers).status_code == 200

assert member.delete(f"/api/content/{post_id}", headers=member_headers).status_code == 204
assert member.get(f"/api/content/{post_id}").status_code == 404
assert member.delete(f"/api/activities/{activity_id}", headers=member_headers).status_code == 204
assert member.delete(f"/api/help-requests/{help_id}", headers=member_headers).status_code == 204
assert member.post("/api/auth/logout", headers=member_headers).status_code == 204
assert member.get("/api/auth/session").status_code == 401

member.close(); volunteer.close(); moderator.close()
print("PASS: Vite proxy -> FastAPI -> PostgreSQL main flows (auth, content, comments, events, activities, help, reports, soft deletion)")
