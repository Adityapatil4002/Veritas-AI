import json
import httpx

class QuestionManager:
    """
    Manages loading and dynamically generating questions for the oral exam using the Gemini API.
    """
    def __init__(self, filepath=None):
        self.api_key = "AIzaSyDSA9Dytf5hbtbG-hKYVbe0mCW9ZC0o0TE"
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.api_key}"
        self.fallback_questions = self._load_fallback_questions(filepath) if filepath else {}

    def _load_fallback_questions(self, filepath):
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    async def generate_question_with_ai(self, domain, difficulty="medium", asked_questions=None):
        """
        Generates a new, unique question using the Gemini AI model.
        """
        if asked_questions is None:
            asked_questions = []

        prompt = f"""
        You are an expert question creator for a university-level oral exam.
        Your task is to generate a single, unique exam question based on the provided criteria.

        Domain: "{domain}"
        Difficulty: "{difficulty}"
        Previously Asked Questions: {json.dumps(asked_questions)}

        Please generate a new question that has NOT been asked before.
        Provide the output in a single, clean JSON object with the following keys:
        1. "question": A string containing the question.
        2. "answer": A string containing the ideal, comprehensive answer.
        3. "keywords": A list of 5-7 essential string keywords from the answer.
        """
        
        payload = {"contents": [{"role": "user", "parts": [{"text": prompt}]}]}
        
        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.post(self.api_url, json=payload)
                response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
                result = response.json()

            if (result.get('candidates') and result['candidates'][0].get('content') and
                result['candidates'][0]['content'].get('parts') and result['candidates'][0]['content']['parts'][0].get('text')):
                
                question_json_str = result['candidates'][0]['content']['parts'][0]['text']
                cleaned_json_str = question_json_str.strip().replace('```json', '').replace('```', '').strip()
                return json.loads(cleaned_json_str)
            else:
                print("Error: AI response format for question generation is invalid.")
                print("Full AI Response:", result)
                return None
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred during question generation: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            print(f"An error occurred during AI question generation: {e}")
            return None
