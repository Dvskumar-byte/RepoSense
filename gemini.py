import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def get_gemini_response(prompt: str) -> str:
    try:
        # We are using 'gemini-flash-latest' from your debug list
        # We remove the 'models/' prefix because the SDK adds it automatically
        response = client.models.generate_content(
            model="gemini-flash-latest", 
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"API Error: {str(e)}"

if __name__ == "__main__":
    # Test it: python gemini.py
    print(get_gemini_response("I updated my model! Are you there?"))