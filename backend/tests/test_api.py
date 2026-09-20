import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import init_db

@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    await init_db()

@pytest.mark.asyncio
async def test_root_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/")
        assert res.status_code == 200
        data = res.json()
        assert "app" in data
        assert data["health_check"] == "/api/health"

@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert "database_mode" in data
        assert "ollama_status" in data

@pytest.mark.asyncio
async def test_session_lifecycle():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Create session
        create_res = await client.post("/api/sessions", json={"title": "Test PM Session"})
        assert create_res.status_code == 201
        session_data = create_res.json()
        session_id = session_data["id"]
        assert session_data["title"] == "Test PM Session"

        # 2. Get session
        get_res = await client.get(f"/api/sessions/{session_id}")
        assert get_res.status_code == 200
        detail = get_res.json()
        assert detail["id"] == session_id
        assert "messages" in detail

        # 3. List sessions
        list_res = await client.get("/api/sessions")
        assert list_res.status_code == 200
        sessions = list_res.json()
        assert any(s["id"] == session_id for s in sessions)

        # 4. Delete session
        del_res = await client.delete(f"/api/sessions/{session_id}")
        assert del_res.status_code == 204

        # 5. Confirm deletion
        confirm_res = await client.get(f"/api/sessions/{session_id}")
        assert confirm_res.status_code == 404
