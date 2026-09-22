from fastapi.testclient import TestClient

from app.main import app
from .conftest import headers, login


def test_auth_csrf_and_content_flow(api):
    assert api.get("/api/content").status_code == 401
    csrf = login(api)
    assert api.get("/api/auth/session").json()["user"]["username"] == "SunlitKoi"
    payload = {"title": "Preparing for a new school year", "body": "This is a synthetic example question for other caregivers.", "format": "Question", "topic": "School and childcare", "stage": "Primary school"}
    assert api.post("/api/content", json=payload).status_code == 403
    created = api.post("/api/content", json=payload, headers=headers(csrf))
    assert created.status_code == 201, created.text
    item = created.json()
    assert item["author"] == "SunlitKoi" and not item["verified"]
    item_id = item["id"]
    assert api.put(f"/api/content/{item_id}/save", headers=headers(csrf)).status_code == 204
    assert api.put(f"/api/content/{item_id}/reaction", headers=headers(csrf)).status_code == 204
    assert api.get(f"/api/content/{item_id}").json()["saved"] is True
    assert api.get(f"/api/content/{item_id}").json()["reactions"] == 1
    comment = api.post(f"/api/content/{item_id}/comments", json={"body": "Thank you for sharing this example."}, headers=headers(csrf))
    assert comment.status_code == 201, comment.text
    reply = api.post(f"/api/content/{item_id}/comments", json={"body": "A synthetic reply.", "parent_id": comment.json()["id"]}, headers=headers(csrf))
    assert reply.status_code == 201
    assert len(api.get(f"/api/content/{item_id}/comments").json()) == 2
    assert api.delete(f"/api/content/{item_id}", headers=headers(csrf)).status_code == 204
    assert api.get(f"/api/content/{item_id}").status_code == 404
    assert all(row["id"] != item_id for row in api.get("/api/content").json())
    assert api.post("/api/auth/logout", headers=headers(csrf)).status_code == 204
    assert api.get("/api/auth/session").status_code == 401


def test_patient_contact_validation_and_permissions(api):
    csrf = login(api)
    payload = {"title": "Call me on 8123 4567", "body": "This is a synthetic example with forbidden contact text.", "format": "Question", "topic": "Travel", "stage": "Primary school"}
    assert api.post("/api/content", json=payload, headers=headers(csrf)).status_code == 422
    assert api.delete("/api/content/1", headers=headers(csrf)).status_code == 403
    assert api.get("/api/reports").status_code == 403
    assert api.post("/api/help-requests", json={"title": "Example help request", "description": "Help with an everyday task.", "area": "Bedok", "non_medical_acknowledged": False}, headers=headers(csrf)).status_code == 422
    assert api.post("/api/activities", json={"title": "Example activity", "description": "A synthetic community activity.", "kind": "Meetup", "starts_at": "2099-10-10T10:00:00", "location": "Bedok"}, headers=headers(csrf)).status_code == 422


def test_events_activities_help_and_moderation(api):
    member_csrf = login(api)
    assert api.put("/api/events/1/registration", headers=headers(member_csrf)).status_code == 204
    assert api.get("/api/events").json()[0]["registered"] is True
    assert api.delete("/api/events/1/registration", headers=headers(member_csrf)).status_code == 204
    activity = api.post("/api/activities", json={"title": "Example coffee meetup", "description": "A synthetic community conversation.", "kind": "Meetup", "starts_at": "2099-11-10T10:00:00Z", "location": "Near Bedok MRT"}, headers=headers(member_csrf))
    assert activity.status_code == 201, activity.text
    assert api.put(f"/api/activities/{activity.json()['id']}/join", headers=headers(member_csrf)).status_code == 204
    assert api.get("/api/activities").json()[-1]["joined"] is True
    req = api.post("/api/help-requests", json={"title": "Collect example supplies", "description": "A synthetic non-medical errand.", "area": "Bedok", "non_medical_acknowledged": True}, headers=headers(member_csrf))
    assert req.status_code == 201, req.text
    req_id = req.json()["id"]
    report = api.post("/api/reports", json={"target_type": "help_request", "target_id": req_id, "reason": "privacy", "details": "Please review this synthetic example."}, headers=headers(member_csrf))
    assert report.status_code == 201, report.text

    with TestClient(app) as other:
        volunteer_csrf = login(other, "BrightKite")
        assert other.post(f"/api/help-requests/{req_id}/cancel", headers=headers(volunteer_csrf)).status_code == 403
        offer = other.post(f"/api/help-requests/{req_id}/offers", headers=headers(volunteer_csrf))
        assert offer.status_code == 201, offer.text
        assert other.get(f"/api/help-requests/{req_id}").json()["offers"] == []
        with TestClient(app) as mod:
            mod_csrf = login(mod, "HSSModerator")
            listed = mod.get("/api/reports")
            assert listed.status_code == 200 and len(listed.json()) == 1
            assert mod.patch(f"/api/reports/{report.json()['id']}", json={"status": "reviewed"}, headers=headers(mod_csrf)).json()["status"] == "reviewed"
    assert api.post(f"/api/help-requests/{req_id}/offers/{offer.json()['id']}/accept", headers=headers(member_csrf)).status_code == 204
    assert api.get(f"/api/help-requests/{req_id}").json()["status"] == "connected"
    with TestClient(app) as uninvolved:
        login(uninvolved, "CalmOtter")
        assert uninvolved.get(f"/api/help-requests/{req_id}").status_code == 403
        assert all(x["id"] != req_id for x in uninvolved.get("/api/help-requests").json())


def test_offer_withdrawal_and_connected_request_visibility(api):
    member_csrf = login(api)
    req = api.post("/api/help-requests", json={"title": "Synthetic local errand", "description": "A synthetic non-medical community task.", "area": "Bedok", "non_medical_acknowledged": True}, headers=headers(member_csrf))
    req_id = req.json()["id"]
    with TestClient(app) as other:
        other_csrf = login(other, "BrightKite")
        assert other.post(f"/api/help-requests/{req_id}/offers", headers=headers(other_csrf)).status_code == 201
        assert other.delete(f"/api/help-requests/{req_id}/offers/mine", headers=headers(other_csrf)).status_code == 204
        offer = other.post(f"/api/help-requests/{req_id}/offers", headers=headers(other_csrf))
        assert offer.status_code == 201
        assert api.post(f"/api/help-requests/{req_id}/offers/{offer.json()['id']}/accept", headers=headers(member_csrf)).status_code == 204
        assert other.get(f"/api/help-requests/{req_id}").status_code == 200
        assert other.delete(f"/api/help-requests/{req_id}/offers/mine", headers=headers(other_csrf)).status_code == 409
    assert api.delete(f"/api/help-requests/{req_id}", headers=headers(member_csrf)).status_code == 204
    assert api.get(f"/api/help-requests/{req_id}").status_code == 404
