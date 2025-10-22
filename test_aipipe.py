# test_aipipe.py
import os
import httpx
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

async def test_aipipe():
    aipipe_key = os.getenv("AIPIPE_API_KEY")

    if not aipipe_key:
        print("❌ AIPipe API key not found in environment variables")
        return False

    # Remove the condition that checks for placeholder text
    print("🧪 Testing AIPipe connection...")
    print(f"🔑 Key loaded: {len(aipipe_key)} characters")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://aipipe.org/openrouter/v1/responses",
                headers={
                    "Authorization": f"Bearer {aipipe_key}",
                    "Content-Type": "application/json",
                    "Referer": "https://github.com/harshvk25/ai-app-builder",
                },
                json={
                    "model": "openai/gpt-4",
                    "input": "Say 'Hello World' in Python",
                    "max_tokens": 50,
                    "temperature": 0.7
                },
                timeout=30.0
            )

            if response.status_code == 200:
                result = response.json()
                print("✅ AIPipe connection successful!")

                # Check response format
                if "output" in result:
                    print(f"📨 Response (output): {result['output']}")
                elif "choices" in result and len(result["choices"]) > 0:
                    print(f"📨 Response (choices): {result['choices'][0].get('message', {}).get('content', '')}")
                else:
                    print(f"📨 Response format: {list(result.keys())}")

                return True
            else:
                print(f"❌ AIPipe returned {response.status_code}: {response.text}")
                return False

    except Exception as e:
        print(f"❌ AIPipe connection failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_aipipe())
