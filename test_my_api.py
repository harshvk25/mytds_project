# test_my_api.py
import requests


def test_evaluation_api():
    print("🔍 Testing Evaluation API Connection...")

    # Test 1: Health endpoint
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        print(f"Health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

    # Test 2: Try to send a mock evaluation
    eval_data = {
        "email": "test@example.com",
        "task": "test-task",
        "round": 1,
        "nonce": "test-nonce",
        "repo_url": "https://github.com/test/repo",
        "commit_sha": "abc123",
        "pages_url": "https://test.github.io/repo"
    }

    try:
        response = requests.post(
            "http://localhost:8001/evaluate",
            json=eval_data,
            timeout=5
        )
        print(f"Evaluation endpoint: {response.status_code} - {response.json()}")
        return True
    except Exception as e:
        print(f"Evaluation endpoint failed: {e}")
        return False


if __name__ == "__main__":
    test_evaluation_api()
