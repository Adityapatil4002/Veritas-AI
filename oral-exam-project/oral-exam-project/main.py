import asyncio
from oral_exam_ai.exam_bot import OralExamAI

# Define the path to the question bank (used as a fallback)
QUESTIONS_FILE_PATH = "data/questions.json"

def main():
    """
    The main function to run the oral exam application.
    """
    print("--- Oral Exam AI Initializing ---")
    
    # Get student's details
    student_name = input("Please enter your name: ")
    domain = input(f"Hello {student_name}, what is your domain of study? (e.g., Networking, Operating Systems): ")
    
    # Create an instance of the OralExamAI
    exam_ai = OralExamAI(QUESTIONS_FILE_PATH)
    
    # Start the exam
    exam_ai.conduct_exam(student_name, domain)
    
    print("\n--- Exam Finished ---")


if __name__ == "__main__":
    # This ensures the main function is called only when the script is executed directly
    main()
