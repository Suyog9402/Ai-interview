import os
from dotenv import load_dotenv
load_dotenv()
from groq import Groq
import google.generativeai as genai

groq_key = os.getenv('GROQ_API_KEY')
gemini_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')

print("=" * 60)
print("Listing Groq Models:")
client = Groq(api_key=groq_key)
try:
    models = client.models.list()
    groq_model_ids = [m.id for m in models.data]
    print("[+] Available Groq models:", groq_model_ids)
    
    # Try chat with first available model
    test_model = groq_model_ids[0] if groq_model_ids else "llama-3.1-8b-instant"
    chat = client.chat.completions.create(
        messages=[{"role": "user", "content": "Hi"}],
        model=test_model
    )
    print(f"[+] Groq chat with {test_model} succeeded: {chat.choices[0].message.content.strip()}")
except Exception as e:
    print("[-] Groq error:", e)

print("=" * 60)
print("Listing Gemini Models:")
genai.configure(api_key=gemini_key)
try:
    gem_models = []
    embed_models = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            gem_models.append(m.name)
        if 'embedContent' in m.supported_generation_methods:
            embed_models.append(m.name)
    print("[+] Available Gemini Chat Models:", gem_models)
    print("[+] Available Gemini Embed Models:", embed_models)
    
    if gem_models:
        test_m = gem_models[0]
        model = genai.GenerativeModel(test_m)
        resp = model.generate_content("Hi")
        print(f"[+] Gemini chat with {test_m} succeeded: {resp.text.strip()}")
    
    if embed_models:
        emb_m = embed_models[0]
        emb = genai.embed_content(model=emb_m, content="Hello")
        print(f"[+] Gemini embed with {emb_m} succeeded, dim: {len(emb['embedding'])}")
except Exception as e:
    print("[-] Gemini error:", e)
print("=" * 60)
