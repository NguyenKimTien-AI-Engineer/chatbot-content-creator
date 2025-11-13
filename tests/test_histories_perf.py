import os
import uuid
import time
import pytest
from fastapi.testclient import TestClient

from app import app


client = TestClient(app)


@pytest.mark.skipif(not os.getenv("MONGODB_CONNECTION"), reason="MongoDB not configured")
def test_append_performance_small_batch():
    conversation_id = f"perf-{uuid.uuid4()}"
    user_id = "perf-user"
    # create
    client.post(
        "/api/v1/histories/create",
        json={"conversation_id": conversation_id, "user_id": user_id},
    )

    # append 200 messages
    start = time.time()
    for i in range(200):
        r = client.post(
            "/api/v1/histories/append",
            json={
                "conversation_id": conversation_id,
                "message": {"role": "assistant", "content": f"msg {i}"},
            },
        )
        assert r.status_code == 200
    elapsed = time.time() - start
    # Expect under 5 seconds on a typical dev Mongo; adjust if needed
    assert elapsed < 5.0