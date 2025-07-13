import json
import httpx

class Evaluator:
    """
    Handles the AI-powered evaluation of a student's answers using the Gemini API.
    """
    def __init__(self):
        self.api_key = "AIzaSyDSA9Dytf5hbtbG-hKYVbe0mCW9ZC0o0TE"
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.api_key}"

    async def evaluate_answer_with_ai(self, question, ideal_answer, student_answer):
        """
        Evaluates the student's answer using the Gemini AI model.
        """
        prompt = f"""
        You are an expert university examiner. Your task is to evaluate a student's answer to a question.
        
        Question: "{question}"
        Ideal Answer for reference: "{ideal_answer}"
        Student's Answer: "{student_answer}"
        
        Please evaluate the student's answer and provide the following in a JSON format:
        1. "evaluation": A string, must be one of "correct", "partially_correct", or "incorrect".
        2. "feedback": A concise explanation for your evaluation. If the answer is not correct, explain what is missing or wrong and provide the correct information.
        3. "score": A float between 0.0 (completely wrong) and 1.0 (perfectly correct).
        """
        
        payload = {"contents": [{"role": "user", "parts": [{"text": prompt}]}]}

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.post(self.api_url, json=payload)
                response.raise_for_status()
                result = response.json()

            if (result.get('candidates') and result['candidates'][0].get('content') and
                result['candidates'][0]['content'].get('parts') and result['candidates'][0]['content']['parts'][0].get('text')):
                
                evaluation_json_str = result['candidates'][0]['content']['parts'][0]['text']
                cleaned_json_str = evaluation_json_str.strip().replace('```json', '').replace('```', '').strip()
                return json.loads(cleaned_json_str)
            else:
                print("Error: AI response format is invalid.")
                print("Full AI Response:", result)
                return {"evaluation": "error", "feedback": "Could not evaluate the answer due to an API error.", "score": 0.0}
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred during evaluation: {e.response.status_code} - {e.response.text}")
            return {"evaluation": "error", "feedback": f"API request failed with status {e.response.status_code}.", "score": 0.0}
        except Exception as e:
            print(f"An error occurred during AI evaluation: {e}")
            return {"evaluation": "error", "feedback": "An error occurred while contacting the evaluation service.", "score": 0.0}
