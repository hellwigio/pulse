import pytest
from sqlalchemy import text

from pulse import create_app
from pulse.models import db


@pytest.fixture
def client():
    app = create_app("pulse.config.TestingConfig")
    with app.app_context():
        db.session.execute(text("PRAGMA foreign_keys=ON"))
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


@pytest.mark.parametrize("resource,payload,update", [
    ("questions", {"text": "First question?"}, {"text": "Updated question?"}),
    ("answers", {"is_agree": True, "question_id": 1}, {"is_agree": False}),
    ("categories", {"name": "General", "question_id": 1}, {"name": "Other"}),
])
def test_crud(client, resource, payload, update):
    if resource != "questions":
        assert client.post("/questions", json={"text": "Parent question?"}).status_code == 201
    url = f"/{resource}"
    assert client.get(url).json == []
    created = client.post(url, json=payload)
    assert created.status_code == 201
    expected = {**payload, "id": created.json["id"]}
    assert created.json == expected
    item = f'{url}/{expected["id"]}'
    assert client.get(item).json == expected
    assert client.get(url).json == [expected]
    patched = client.patch(item, json=update)
    assert patched.status_code == 200
    assert patched.json == {**expected, **update}
    assert client.patch(item, json={}).json == patched.json
    replaced = client.put(item, json=payload)
    assert replaced.status_code == 200
    assert replaced.json == expected
    deleted = client.delete(item)
    assert deleted.status_code == 204
    assert deleted.data == b""
    assert client.get(item).status_code == 404
    assert client.get(url).json == []


@pytest.mark.parametrize("resource", ["questions", "answers", "categories"])
@pytest.mark.parametrize("method", ["get", "put", "patch", "delete"])
def test_missing_record(client, resource, method):
    response = getattr(client, method)(f"/{resource}/999", json={})
    assert response.status_code == 404
    assert "error" in response.json


@pytest.mark.parametrize("resource,payload,field", [
    ("questions", {"text": "Question?"}, "text"),
    ("answers", {"is_agree": True, "question_id": 1}, "is_agree"),
    ("categories", {"name": "General", "question_id": 1}, "name"),
])
def test_validation(client, resource, payload, field):
    if resource != "questions":
        client.post("/questions", json={"text": "Parent question?"})
    url = f"/{resource}"
    assert client.post(url, json={}).status_code == 422
    assert client.post(url, json={**payload, "unexpected": 1}).status_code == 422
    assert client.post(url, json={**payload, field: None}).status_code == 422
    assert client.post(url, json=[]).status_code == 422
    assert client.post(url, data="null", content_type="application/json").status_code == 422
    assert client.post(url, data="{", content_type="application/json").status_code == 400
    assert client.post(url, data="plain text").status_code == 415
    created = client.post(url, json=payload)
    item = f'{url}/{created.json["id"]}'
    assert client.put(item, json={}).status_code == 422
    for invalid in [{field: None}, {"id": 2}, {field: []}]:
        response = client.patch(item, json=invalid)
        assert response.status_code == 422
        assert "error" in response.json
    assert client.get(item).json == created.json


@pytest.mark.parametrize("resource,payload", [
    ("answers", {"is_agree": False}),
    ("categories", {"name": "General"}),
])
def test_question_references_and_delete_conflict(client, resource, payload):
    url = f"/{resource}"
    assert client.post(url, json={**payload, "question_id": 999}).status_code == 404
    assert client.post(url, json={**payload, "question_id": 0}).status_code == 422
    first = client.post("/questions", json={"text": "First question?"}).json["id"]
    second = client.post("/questions", json={"text": "Second question?"}).json["id"]
    created = client.post(url, json={**payload, "question_id": first})
    item = f'{url}/{created.json["id"]}'
    assert client.delete(f"/questions/{first}").status_code == 409
    assert client.get(f"/questions/{first}").status_code == 200
    assert client.patch(item, json={"question_id": 999}).status_code == 404
    assert client.patch(item, json={"question_id": None}).status_code == 422
    assert client.get(item).json["question_id"] == first
    assert client.patch(item, json={"question_id": second}).status_code == 200
    assert client.delete(f"/questions/{first}").status_code == 204
    assert client.delete(f"/questions/{second}").status_code == 409
    assert client.delete(item).status_code == 204
    assert client.delete(f"/questions/{second}").status_code == 204


def test_category_conflicts(client):
    for name in ["First question?", "Second question?"]:
        client.post("/questions", json={"text": name})
    first = client.post("/categories", json={"name": "First", "question_id": 1})
    assert first.status_code == 201
    assert client.post("/categories", json={"name": "Duplicate", "question_id": 1}).status_code == 409
    second = client.post("/categories", json={"name": "Second", "question_id": 2})
    item = f'/categories/{second.json["id"]}'
    assert client.patch(item, json={"question_id": 1}).status_code == 409
    assert client.get(item).json == second.json
    assert client.patch(item, json={"question_id": 2}).status_code == 200


@pytest.mark.parametrize("url,payload", [
    ("/questions", {"text": "  "}),
    ("/questions", {"text": "ab"}),
    ("/questions", {"text": "a" * 256}),
    ("/categories", {"name": "  ", "question_id": 1}),
    ("/answers", {"is_agree": "invalid", "question_id": 1}),
])
def test_invalid_values(client, url, payload):
    assert client.post(url, json=payload).status_code == 422


def test_trim_question(client):
    response = client.post("/questions", json={"text": "  Question?  "})
    assert response.status_code == 201
    assert response.json["text"] == "Question?"
