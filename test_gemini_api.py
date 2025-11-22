#!/usr/bin/env python3
"""Test rapido Gemini API"""
import os
import requests

api_key = os.getenv('GOOGLE_API_KEY')

if not api_key:
    print("❌ GOOGLE_API_KEY non settata!")
    print("   Esegui: export GOOGLE_API_KEY='tua-chiave'")
    exit(1)

print(f"✓ API Key trovata (lunghezza: {len(api_key)} caratteri)")
print("🔄 Testing Gemini API...")

url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent"

headers = {
    "Content-Type": "application/json",
    "x-goog-api-key": api_key
}

data = {
    "contents": [{
        "parts": [{"text": "Rispondi solo con 'OK' se funzioni."}]
    }]
}

try:
    response = requests.post(url, headers=headers, json=data, timeout=10)

    if response.status_code == 200:
        result = response.json()
        text = result['candidates'][0]['content']['parts'][0]['text']
        print(f"✅ API FUNZIONA! Risposta: {text.strip()}")
    else:
        print(f"❌ Errore {response.status_code}")
        print(f"   {response.text}")

except Exception as e:
    print(f"❌ Errore: {e}")
