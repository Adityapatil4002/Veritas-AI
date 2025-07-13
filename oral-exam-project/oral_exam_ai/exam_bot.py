import asyncio
import json
import httpx
import os # Import os to check for profile existence
from .question_manager import QuestionManager
from .evaluator import Evaluator
from .results_saver import ResultsSaver
from .profile_manager import ProfileManager # Import the new profile manager

class OralExamAI:
    """
    The main class that orchestrates the AI-powered oral examination process
    with student profiles and history.
    """
    def __init__(self, questions_filepath=None):
        self.question_manager = QuestionManager(questions_filepath)
        self.evaluator = Evaluator()
        self.results_saver = ResultsSaver()
        self.profile_manager = ProfileManager() # Initialize the profile manager
        self.api_key = "AIzaSyDSA9Dytf5hbtbG-hKYVbe0mCW9ZC0o0TE"
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.api_key}"

    async def _get_ai_response(self, prompt):
        """A helper function to get a response from the Gemini API."""
        payload = {"contents": [{"role": "user", "parts": [{"text": prompt}]}]}
        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.post(self.api_url, json=payload)
                response.raise_for_status()
                result = response.json()
                if (result.get('candidates') and result['candidates'][0].get('content') and
                    result['candidates'][0]['content'].get('parts') and result['candidates'][0]['content']['parts'][0].get('text')):
                    return result['candidates'][0]['content']['parts'][0]['text']
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            print(f"An error occurred during AI interaction: {e}")
        return None

    async def _handle_conversation(self, question_text, domain):
        # This method remains the same as the previous version
        print(f"Question: {question_text}")
        while True:
            user_input = input("Your response: ")
            intent_prompt = f"""Analyze the student's response to determine their intent. The original question was about "{domain}". Student's response: "{user_input}" Classify the intent into one of these categories: "providing_answer", "request_rephrase", "request_definition", "request_hint". Return a single JSON object with two keys: "intent" and, if the intent is "request_definition", a "term" key with the term they want defined."""
            intent_response = await self._get_ai_response(intent_prompt)
            try:
                intent_data = json.loads(intent_response.strip().replace('```json', '').replace('```', ''))
                intent = intent_data.get("intent")
            except (json.JSONDecodeError, AttributeError):
                intent = "providing_answer"
            if intent == "providing_answer": return user_input
            elif intent == "request_rephrase":
                rephrased_q = await self._get_ai_response(f"The student is confused by this question: '{question_text}'. Rephrase it to be clearer or simpler, without giving away the answer.")
                print(f"Of course, let me rephrase: {rephrased_q}")
            elif intent == "request_hint":
                hint = await self._get_ai_response(f"The student needs a hint for the question: '{question_text}'. Provide a conceptual hint that guides them toward the answer without giving it away directly.")
                print(f"Here's a hint for you: {hint}")
            elif intent == "request_definition":
                term = intent_data.get("term", "that term")
                definition = await self._get_ai_response(f"In the context of {domain}, briefly define the term '{term}' for a student.")
                print(f"Certainly. {definition}")
            print("\nLet's try the question again.")

    async def conduct_exam_async(self, student_name, domain, num_questions=5):
        """Conducts the exam, now using student history to guide questions."""
        # Load student profile and greet them
        student_profile = self.profile_manager.load_profile(student_name)
        if student_profile.get("history"):
            print(f"\nWelcome back, {student_name}! We'll pick up where you left off.")
        else:
            print(f"\nHello {student_name}, let's create your profile and begin.")
        
        historical_questions = [item['question'] for item in student_profile.get('history', [])]
        print(f"You have answered {len(historical_questions)} questions in the past. We will not repeat them.")

        exam_records, difficulty_levels, current_difficulty_index = [], ["easy", "medium", "hard"], 1
        
        for i in range(num_questions):
            difficulty = difficulty_levels[current_difficulty_index]
            print(f"\n--- Question {i+1}/{num_questions} (Difficulty: {difficulty}) ---")

            q_data = await self.question_manager.generate_question_with_ai(domain, difficulty, historical_questions)
            if not q_data:
                print("Failed to generate a unique question. Please check API key/connection. Ending exam.")
                break
            
            historical_questions.append(q_data["question"]) # Add to history to avoid repeats in the same session
            user_answer = await self._handle_conversation(q_data['question'], domain)
            evaluation = await self.evaluator.evaluate_answer_with_ai(q_data['question'], q_data['answer'], user_answer)
            record = {"question": q_data['question'], "student_answer": user_answer, **evaluation}
            exam_records.append(record)

            print(f"\nEvaluation: {record.get('evaluation', 'error').replace('_', ' ').title()}")
            print(f"Feedback: {record.get('feedback', 'No feedback provided.')}")
            
            score = record.get('score', 0.0)
            if score > 0.75 and current_difficulty_index < len(difficulty_levels) - 1: current_difficulty_index += 1; print("(Difficulty will increase)")
            elif score < 0.4 and current_difficulty_index > 0: current_difficulty_index -= 1; print("(Difficulty will decrease)")

        self._display_results(student_name, exam_records)
        
        # Update profile with new records and save
        student_profile["history"].extend(exam_records)
        self.profile_manager.save_profile(student_name, student_profile)
        
        # Also save to the general CSV log
        self.results_saver.save_results(student_name, domain, exam_records)

    def conduct_exam(self, student_name, domain, num_questions=5):
        """Synchronous wrapper to run the async exam."""
        try:
            asyncio.run(self.conduct_exam_async(student_name, domain, num_questions))
        except KeyboardInterrupt: print("\nExam interrupted by user.")
        finally: print("\n--- Exam session concluded. ---")

    def _display_results(self, student_name, records):
        """Calculates and displays the final results for the student for the current session."""
        print(f"\n--- Current Session Results for {student_name} ---")
        total_score = sum(r.get('score', 0) for r in records)
        total_possible = len(records)
        if total_possible > 0:
            final_percentage = (total_score / total_possible) * 100
            grade = self._get_grade_from_percentage(final_percentage)
            print(f"Session Score: {total_score:.2f} / {total_possible:.2f}")
            print(f"Session Percentage: {final_percentage:.2f}%")
            print(f"Session Grade: {grade}")
        else:
            print("\nNo questions were processed in this session.")

    def _get_grade_from_percentage(self, percentage):
        """Assigns a letter grade based on a percentage score."""
        if percentage >= 90: return "A (Excellent)"
        elif percentage >= 80: return "B (Good)"
        elif percentage >= 70: return "C (Average)"
        elif percentage >= 60: return "D (Pass)"
        else: return "F (Fail)"
