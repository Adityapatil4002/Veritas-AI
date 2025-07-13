import csv
import os
from datetime import datetime

class ResultsSaver:
    """
    Handles saving the detailed results of an oral exam to a CSV file.
    """
    def __init__(self, filepath="exam_results.csv"):
        """
        Initializes the ResultsSaver.

        Args:
            filepath (str): The path to the CSV file where results will be saved.
        """
        self.filepath = filepath

    def save_results(self, student_name, domain, exam_data):
        """
        Saves the results of a single exam to the CSV file.

        Args:
            student_name (str): The name of the student.
            domain (str): The domain/subject of the exam.
            exam_data (list): A list of dictionaries, where each dict contains the
                              details of a single question-answer interaction.
        """
        # Check if the file exists to determine if we need to write headers
        file_exists = os.path.isfile(self.filepath)

        try:
            with open(self.filepath, 'a', newline='', encoding='utf-8') as csvfile:
                # Define the columns for our CSV file
                fieldnames = [
                    'timestamp', 'student_name', 'domain', 'question', 
                    'student_answer', 'evaluation', 'feedback', 'score'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                if not file_exists:
                    writer.writeheader()  # Write header only if file is new

                # Get the current time for the timestamp
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                for record in exam_data:
                    row = {
                        'timestamp': timestamp,
                        'student_name': student_name,
                        'domain': domain,
                        'question': record.get('question', ''),
                        'student_answer': record.get('student_answer', ''),
                        'evaluation': record.get('evaluation', ''),
                        'feedback': record.get('feedback', ''),
                        'score': record.get('score', 0.0)
                    }
                    writer.writerow(row)
            
            print(f"\nSuccessfully saved exam results to {self.filepath}")

        except IOError as e:
            print(f"\nError: Could not write to file {self.filepath}. {e}")

