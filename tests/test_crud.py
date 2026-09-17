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
    ("categories", {"name": "General"}, {"name": "Other"}),
])
def test_crud(client, resource, payload, update):
    if resource != "questions":
        assert client.post("/questions", json={"text": "Parent question?"}).status_code == 201
    url = f"/{resource}"
    assert client.get(url).json == []
    created = client.post(url, json=payload)
    assert created.status_code == 201
    expected = {**payload, "id": created.json["id"]}
    if resource == "questions":
        expected.update(category_id=None, category=None)
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
    ("categories", {"name": "General"}, "name"),
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


def test_question_categories(client):
    category = client.post('/categories', json={'name': '  General  '}).json
    assert category == {'id': 1, 'name': 'General'}
    for title in ['First question?', 'Second question?']:
        response = client.post('/questions', json={'text': title, 'category_id': 1})
        assert response.status_code == 201
        assert response.json['category'] == category
        assert response.json['category_id'] == 1
    assert all(q['category'] == category for q in client.get('/questions').json)
    assert client.delete('/categories/1').status_code == 409
    assert client.put('/categories/1', json={'name': 'Updated'}).status_code == 200
    assert client.get('/questions/1').json['category']['name'] == 'Updated'
    assert client.patch('/questions/1', json={'category_id': None}).json['category'] is None
    assert client.patch('/questions/2', json={'text': 'Changed question?'}).json['category_id'] == 1
    other = client.post('/categories', json={'name': 'Other'}).json
    assert client.patch('/questions/2', json={'category_id': other['id']}).json['category'] == other
    assert client.put('/questions/2', json={'text': 'Replacement question?'}).json['category'] is None
    assert client.delete('/categories/1').status_code == 204
    assert client.post('/questions', json={'text': 'Categorized?', 'category_id': other['id']}).status_code == 201
    assert client.delete('/questions/3').status_code == 204
    assert client.get(f'/categories/{other["id"]}').status_code == 200


@pytest.mark.parametrize('category_id,status', [(999, 404), (0, 422), (-1, 422), ('bad', 422)])
def test_invalid_category_reference(client, category_id, status):
    assert client.post('/questions', json={'text': 'Question?', 'category_id': category_id}).status_code == status
    question = client.post('/questions', json={'text': 'Question?'}).json
    for method in ['put', 'patch']:
        response = getattr(client, method)('/questions/1', json={'text': 'Changed?', 'category_id': category_id})
        assert response.status_code == status
        assert client.get('/questions/1').json == question
