from dotenv import load_dotenv
load_dotenv()

groq_key = os.getenv('GROQ_API_KEY')
gemini_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')

print("=" * 60)
print("Testing Groq...")
try:
    from groq import Groq
    client = Groq(api_key=groq_key)
    chat = client.chat.completions.create(
        messages=[{"role": "user", "content": "Respond with: Groq is working!"}],
        model="llama-3.3-70b-versatile"
    )
    print("[+] Direct Groq Success:", chat.choices[0].message.content.strip())
except Exception as e:
    print("[-] Direct Groq Failed:", e)

print("=" * 60)
print("Testing Gemini GenAI...")
try:
    import google.generativeai as genai
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content("Respond with: Gemini is working!")
    print("[+] Direct Gemini LLM Success:", response.text.strip())
    
    # Test embedding
    result = genai.embed_content(
        model="models/embedding-001",
        content="Test embedding",
        task_type="retrieval_document"
    )
    print("[+] Direct Gemini Embedding (embedding-001) Success, dim:", len(result['embedding']))
except Exception as e:
    print("[-] Direct Gemini Failed:", e)
print("=" * 60)
