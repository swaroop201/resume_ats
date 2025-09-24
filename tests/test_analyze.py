import io
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

JD = """
We are seeking a Python engineer with FastAPI, AWS, Docker, CI/CD, and SQL.
Experience with scikit-learn is a plus. Strong Linux fundamentals required.
""".strip()

RESUME_TXT = """
John Doe
Email: john@example.com
Experience: Built FastAPI services in Python. Docker + AWS ECR/ECS deployments.
Skills: Python, FastAPI, AWS, Docker, Linux, SQL, Git, CI
""".strip()

def test_analyze_txt():
    files = {"files": ("resume.txt", io.BytesIO(RESUME_TXT.encode("utf-8")), "text/plain")}
    data = {"job_description": JD}
    resp = client.post("/api/analyze/", files=files, data=data)
    assert resp.status_code == 200, resp.text
    js = resp.json()
    assert js["results"][0]["score"] >= 0
