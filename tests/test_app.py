import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)
activities = app_module.activities


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_duplicate_and_capacity():
    name = "CI Test Activity"
    # create a temporary activity for the test
    activities[name] = {
        "description": "Temporary activity for CI tests",
        "schedule": "TBA",
        "max_participants": 2,
        "participants": []
    }

    try:
        email = "tester@example.com"

        # signup should succeed
        r = client.post(f"/activities/{name}/signup?email={email}")
        assert r.status_code == 200
        assert email in activities[name]["participants"]

        # duplicate signup should be rejected
        r2 = client.post(f"/activities/{name}/signup?email={email}")
        assert r2.status_code == 400

        # add another participant (fills to capacity)
        r3 = client.post(f"/activities/{name}/signup?email=other1@example.com")
        assert r3.status_code == 200

        # now full: further signup should fail
        r4 = client.post(f"/activities/{name}/signup?email=other2@example.com")
        assert r4.status_code == 400

    finally:
        # clean up
        del activities[name]


def test_remove_participant():
    name = "CI Remove Activity"
    activities[name] = {
        "description": "Temporary activity for remove test",
        "schedule": "TBA",
        "max_participants": 5,
        "participants": ["remove_me@example.com"]
    }

    try:
        # remove should succeed
        res = client.delete(f"/activities/{name}/participants?email=remove_me@example.com")
        assert res.status_code == 200
        assert "remove_me@example.com" not in activities[name]["participants"]

        # removing again should return 404
        res2 = client.delete(f"/activities/{name}/participants?email=remove_me@example.com")
        assert res2.status_code == 404

    finally:
        del activities[name]
