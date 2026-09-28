import json, os, urllib.request
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("GEMINI_API_KEY")
model = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

if not key:
    raise SystemExit("GEMINI_API_KEY is not set. Add it to your .env file.")

req = urllib.request.Request(
    f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
    data=json.dumps({"contents": [{"role": "user", "parts": [{"text": "Say hi"}]}]}).encode(),
    headers={"Content-Type": "application/json", "x-goog-api-key": key},
)
try:
    print(urllib.request.urlopen(req, timeout=60).read().decode()[:500])
except Exception as e:
    print(type(e).__name__, e)
    if hasattr(e, "read"):
        print(e.read().decode())