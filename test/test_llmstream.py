import requests
import os

# 환경 변수에서 기본 설정 로드
BASE_URL = os.getenv("LLMSTREAM_BASE_URL", "http://localhost:8000") # 변경 필요
MODEL_NAME = os.getenv("LLMSTREAM_MODEL_NAME", "gpt-3.5-turbo") # 변경 필요

# 테스트 엔드포인트 및 요청 데이터
TEST_CASES = [
    {
        "endpoint": "/generate",
        "payload": {
            "prompt": "Test generate endpoint",
            "max_tokens": 10,
            "temperature": 0.7
        },
        "description": "Testing /generate endpoint"
    },
    {
        "endpoint": "/v1/chat/completions",
        "payload": {
            "model": MODEL_NAME,
            "messages": [{"role": "user", "content": "Hello, LLMStream!"}],
            "max_tokens": 10,
            "temperature": 0.7
        },
        "description": "Testing /v1/chat/completions endpoint"
    },
    {
        "endpoint": "/v1/completions",
        "payload": {
            "model": MODEL_NAME,
            "prompt": "Test completions endpoint",
            "max_tokens": 10,
            "temperature": 0.7
        },
        "description": "Testing /v1/completions endpoint"
    }
]

def test_llmstream():
    """
    테스트 스크립트를 실행하여 각 엔드포인트에 대한 연결 상태를 확인
    """
    print(f"Starting LLMStream endpoint tests...\nBase URL: {BASE_URL}")
    print(f"Model Name: {MODEL_NAME}\n")
    for case in TEST_CASES:
        url = f"{BASE_URL}{case['endpoint']}"
        payload = case["payload"]
        description = case["description"]

        print(f"Test: {description}")
        print(f"POST {url}")
        try:
            response = requests.post(url, json=payload, timeout=5)
            if response.status_code == 200:
                print(f"✅ SUCCESS: {response.status_code}")
            else:
                print(f"⚠️ WARNING: {response.status_code} - {response.text}")
        except requests.RequestException as e:
            print(f"❌ ERROR: Unable to connect to {url} - {str(e)}")
        print("-" * 50)

if __name__ == "__main__":
    test_llmstream()
