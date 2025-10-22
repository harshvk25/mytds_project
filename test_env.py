# test_env.py
from dotenv import load_dotenv
import os

load_dotenv()

print("🔍 Checking environment variables:")
print(f"SECRET: {os.getenv('SECRET', 'NOT FOUND')}")
print(f"GITHUB_TOKEN: {'FOUND' if os.getenv('GITHUB_TOKEN') else 'NOT FOUND'}")
print(f"AIPIPE_API_KEY: {'FOUND' if os.getenv('AIPIPE_API_KEY') else 'NOT FOUND'}")
