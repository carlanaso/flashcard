import os
import json
import time

QUIZ_FILE = "quiz.txt"
QUIZS_DIR = 'quizs'  # Fixed the directory name

# Ensure the quizs directory exists
os.makedirs(QUIZS_DIR, exist_ok=True)

def process_requests():
    while True:
        time.sleep(1)  # Delay to avoid busy-waiting

        if os.path.exists(QUIZ_FILE):
            try:
                print("Quiz request found. Processing...")

                with open(QUIZ_FILE, 'r') as file:
                    content = file.read().strip()
                os.remove(QUIZ_FILE)  # Remove the file after reading

                if content:
                    print(f"Request content: {content}")
                    lines = content.split('\n')
                    action = lines[0].split(":")[1].strip()
                    if action == "GenerateQuiz":
                        response_message = process_generate_quiz(lines)

                        # Write response to the appropriate file in 'quizs/' directory
                        response_filename = f"{lines[1].split(':')[1].strip().replace(' ', '_')}_quiz.txt"
                        response_file = os.path.join(QUIZS_DIR, response_filename)
                        with open(response_file, "w") as response_file:
                            response_file.write(response_message)
                        print(f"Quiz generated and saved to {response_file}")

            except PermissionError:
                print("Permission error encountered. Retrying...")
                continue


def process_generate_quiz(lines):
    database_name = None
    flashcards = []
    quiz_settings = None

    for line in lines:
        if line.startswith("DatabaseName:"):
            database_name = line.split(":")[1].strip()
        
        elif line.startswith("SelectedFlashcards:"):
            flashcards_json = line.split(":", 1)[1].strip()
            try:
                flashcards = json.loads(flashcards_json)
                print("Parsed Flashcards:", flashcards)
            except json.JSONDecodeError as e:
                return f"Message: Error decoding flashcards JSON - {e}"
        
        elif line.startswith("QuizSettings:"):
            quiz_settings_json = line.split(":", 1)[1].strip()
            try:
                quiz_settings = json.loads(quiz_settings_json)
                print("Parsed Quiz Settings:", quiz_settings)
            except json.JSONDecodeError as e:
                return f"Message: Error decoding quiz settings JSON - {e}"

    print(f"Parsed Data - Database Name: {database_name}, Flashcards: {flashcards}, Quiz Settings: {quiz_settings}")

    if database_name and flashcards and quiz_settings:
        try:
            num_questions = quiz_settings.get("num_questions", len(flashcards))
            questions = flashcards[:num_questions]
            
            if not questions:
                raise ValueError("No questions generated. Flashcards might be empty or num_questions is 0.")
            
            quiz = "\n".join([f"Q: {q['front']}?" for q in questions])

            # Save quiz to file
            quiz_file = os.path.join(QUIZS_DIR, f"{database_name.replace(' ', '_')}_quiz.txt")
            with open(quiz_file, 'w') as file:
                file.write(quiz + '\n')
                file.write("\nAnswers:\n")  # Placeholder for user answers
                file.write("\nPoints:\n")  # Placeholder for points
            
            print(f"Quiz generated and saved to {quiz_file}")
            return quiz  # Return only the quiz questions, not the message
        except Exception as e:
            return f"Message: Error processing the quiz - {e}"
    else:
        return "Message: Invalid quiz request format."


def generate_quiz(flashcards, quiz_settings):
    num_questions = quiz_settings.get("num_questions", len(flashcards))
    questions = flashcards[:num_questions]
    quiz = "\n".join([f"Q: {q['front']}?" for q in questions])
    return questions, quiz

if __name__ == "__main__":
    process_requests()
