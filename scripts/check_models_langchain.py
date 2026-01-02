import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# List available models
import google.generativeai as genai

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

print("Available Gemini models:")
print("="*60)

for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"Name: {m.name}")
        print(f"  Display Name: {m.display_name}")
        print(f"  Description: {m.description[:80]}...")
        print()
