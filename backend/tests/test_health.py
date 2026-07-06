from app.api.routes import healthcheck
from app.core.config import Settings


class FakeDB:
    def execute(self, _query):
        return None


def test_health_endpoint():
    response = healthcheck(
        db=FakeDB(),
        settings=Settings(aws_sqs_queue_url="https://example.com/docops-processing"),
    )
    assert response.status == "ok"
    assert response.database == "ok"
    assert response.queue == "configured"
