import json
import os
import re

class ProfileManager:
    """
    Manages creating, loading, and saving student profiles to JSON files.
    """
    def __init__(self, directory="student_profiles"):
        """
        Initializes the ProfileManager and creates the profile directory if it doesn't exist.
        """
        self.directory = directory
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
            print(f"Created directory for student profiles at: {self.directory}")

    def _sanitize_filename(self, name):
        """
        Sanitizes a student's name to be used as a valid filename.
        Removes special characters and replaces spaces with underscores.
        """
        name = re.sub(r'[^\w\s-]', '', name).strip().lower()
        name = re.sub(r'[-\s]+', '_', name)
        return name

    def _get_profile_path(self, student_name):
        """Constructs the full file path for a student's profile."""
        sanitized_name = self._sanitize_filename(student_name)
        return os.path.join(self.directory, f"{sanitized_name}.json")

    def load_profile(self, student_name):
        """
        Loads a student's profile from a JSON file.

        Args:
            student_name (str): The name of the student.

        Returns:
            dict: A dictionary containing the student's profile data,
                  or a default new profile if one doesn't exist.
        """
        filepath = self._get_profile_path(student_name)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                # Return a default profile if the file is corrupted or unreadable
                return {"student_name": student_name, "history": []}
        # Return a new profile for a new student
        return {"student_name": student_name, "history": []}

    def save_profile(self, student_name, profile_data):
        """
        Saves a student's profile data to a JSON file.

        Args:
            student_name (str): The name of the student.
            profile_data (dict): The profile data to save.
        """
        filepath = self._get_profile_path(student_name)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, indent=4)
            print(f"Student profile for '{student_name}' has been saved/updated.")
        except IOError as e:
            print(f"Error: Could not save profile for '{student_name}'. {e}")
