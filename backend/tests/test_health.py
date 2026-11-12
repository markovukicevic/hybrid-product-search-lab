from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.main import app


def test_liveness():
    with TestClient(app) as client:
        assert client.get("/health/live").json() == {"status": "ok"}


def test_readiness_database_failure():
    with TestClient(app) as client:
        engine = MagicMock()
        engine.connect.side_effect = OperationalError("SELECT 1", {}, Exception("secret"))
        app.state.engine = engine
        response = client.get("/health/ready")
        assert response.status_code == 503
        assert response.json() == {"detail": "Database unavailable"}
