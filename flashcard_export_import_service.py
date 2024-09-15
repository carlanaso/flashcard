import os
import time
import json

EXPORT_REQUEST_FILE = "export.txt"
EXPORTS_DIR = 'exports'
DATABASES_DIR = 'databases'

# Ensure the exports directory exists
os.makedirs(EXPORTS_DIR, exist_ok=True)

def process_requests():
    while True:
        time.sleep(1)  # Delay to avoid busy-waiting
        request_file_path = os.path.join(EXPORTS_DIR, EXPORT_REQUEST_FILE)
        if os.path.exists(request_file_path):
            try:
                with open(request_file_path, 'r') as file:
                    content = file.read().strip()
                os.remove(request_file_path)  # Remove the file after reading

                if content:
                    lines = content.split('\n')
                    action = lines[0].split(":")[1].strip()
                    
                    if action == "ExportFlashcards":
                        response_message = process_export_flashcards(lines)
                        
                        # Write response to EXPORT_REQUEST_FILE in the exports directory
                        with open(request_file_path, 'w') as export_file:
                            export_file.write(response_message + "\n")

            except PermissionError:
                continue

def process_export_flashcards(lines):
    database_name = None
    export_file = None

    for line in lines:
        if line.startswith("DatabaseName:"):
            database_name = line.split(":")[1].strip()
        elif line.startswith("ExportFile:"):
            export_file = line.split(":")[1].strip()

    if database_name and export_file:
        response_message = export_flashcards_and_feedback(database_name, export_file)
    else:
        response_message = "Message: Invalid export format."

    return response_message

def export_flashcards_and_feedback(database_name, export_file):
    database_path = os.path.join(DATABASES_DIR, f"{database_name}.txt")
    feedback_path = os.path.join(DATABASES_DIR, f"{database_name}_reviews.txt")
    
    if not os.path.exists(database_path):
        return f"Message: Database '{database_name}' does not exist."

    export_path = os.path.join(EXPORTS_DIR, export_file)

    with open(export_path, 'w') as file:
        # Export flashcards
        with open(database_path, 'r') as db_file:
            flashcards = db_file.readlines()
        for card in flashcards:
            card = json.loads(card)
            file.write(f"Q: {card['question']}\nA: {card['answer']}\n\n")

        # Export feedback
        if os.path.exists(feedback_path):
            with open(feedback_path, 'r') as fb_file:
                feedbacks = fb_file.readlines()
            file.write("Feedback:\n")
            for feedback in feedbacks:
                file.write(feedback + "\n")
        else:
            file.write("No feedback available.\n")

    # Return a success message
    return f"Message: Successfully exported '{database_name}' flashcard set to {export_file}"

if __name__ == "__main__":
    if not os.path.exists(DATABASES_DIR):
        os.makedirs(DATABASES_DIR)
    process_requests()
