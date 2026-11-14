def test_chat_new_session(client, fake_service):
    r = client.post("/api/v1/chat", json={"message": "hi"})
    assert r.status_code == 200
    assert r.json() == {"session_id": "new-session", "reply": "echo: hi"}
    assert fake_service.calls[0]["session_id"] is None


def test_chat_existing_session(client, fake_service):
    r = client.post("/api/v1/chat", json={"message": "again", "session_id": "s1", "user_id": "u1"})
    assert r.json()["session_id"] == "s1"
    assert fake_service.calls[0] == {"user_id": "u1", "session_id": "s1", "message": "again"}


def test_chat_rejects_empty_message(client):
    assert client.post("/api/v1/chat", json={"message": ""}).status_code == 422
