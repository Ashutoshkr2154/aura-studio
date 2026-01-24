import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

try:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    print("⏳ Testing OpenAI Connection...")
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo", # Use a cheap model for testing
        messages=[{"role": "user", "content": "Say 'Connection Successful'"}],
        max_tokens=10
    )
    print(f"✅ API RESPONSE: {response.choices[0].message.content}")
    print("🎉 Your Key is WORKING PERFECTLY.")
    
except Exception as e:
    print(f"❌ API KEY ERROR: {e}")