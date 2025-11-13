import os
import uuid
import pytest
from fastapi.testclient import TestClient

from app import app


client = TestClient(app)


@pytest.mark.skipif(not os.getenv("MONGODB_CONNECTION"), reason="MongoDB not configured")
def test_create_append_get_history():
    conversation_id = f"pytest-{uuid.uuid4()}"
    user_id = "pytest-user"

    # Create conversation
    r1 = client.post(
        "/api/v1/histories/create",
        json={
            "conversation_id": conversation_id,
            "user_id": user_id,
            "first_message": {
                "role": "user",
                "content": "Xin chao",
            },
            "metadata": {"source": "pytest"},
        },
    )
    assert r1.status_code == 200, r1.text

    # Append assistant reply
    r2 = client.post(
        "/api/v1/histories/append",
        json={
            "conversation_id": conversation_id,
            "message": {
                "role": "assistant",
                "content": "Chao ban",
                "metadata": {"confidence": 0.9},
            },
        },
    )
    assert r2.status_code == 200, r2.text

    # Get conversation
    r3 = client.post(
        "/api/v1/histories/get",
        json={"conversation_id": conversation_id},
    )
    assert r3.status_code == 200, r3.text
    payload = r3.json()
    assert payload["status"] == 200
    doc = payload["data"]
    assert doc["conversation_id"] == conversation_id
    assert doc["user_id"] == user_id
    assert len(doc.get("messages", [])) >= 2


@pytest.mark.skipif(not os.getenv("MONGODB_CONNECTION"), reason="MongoDB not configured")
def test_list_pagination():
    user_id = "pytest-user"
    r = client.post(
        "/api/v1/histories/list",
        json={"user_id": user_id, "page": 1, "limit": 5},
    )
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert "items" in data and isinstance(data["items"], list)
    assert data["page"] == 1
    assert data["limit"] == 5