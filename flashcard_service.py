import os
import json
import time

REQUESTS_DIR = 'requests'
RESPONSES_DIR = 'responses'
DATABASES_DIR = 'databases'

def create_database(database_name):
    database_path = os.path.join(DATABASES_DIR, f"{database_name}.txt")
    if os.path.exists(database_path):
        return f"Database '{database_name}' already exists."
    else:
        with open(database_path, 'w') as db_file:
            db_file.write('')
        return f"Database '{database_name}' created successfully."

def add_flashcard(database_name, question, answer):
    database_path = os.path.join(DATABASES_DIR, f"{database_name}.txt")
    if not os.path.exists(database_path):
        return f"Database '{database_name}' does not exist."
    else:
        with open(database_path, 'a') as db_file:
            db_file.write(json.dumps({'question': question, 'answer': answer}) + '\n')
        return f"Flashcard added successfully to '{database_name}'."

def retrieve_flashcards(database_name):
    database_path = os.path.join(DATABASES_DIR, f"{database_name}.txt")
    if not os.path.exists(database_path):
        return f"Database '{database_name}' does not exist."
    else:
        with open(database_path, 'r') as db_file:
            flashcards = db_file.readlines()
        return {'databaseName': database_name, 'flashcards': [json.loads(card) for card in flashcards]}

def process_requests():
    while True:
        for request_file in os.listdir(REQUESTS_DIR):
            request_path = os.path.join(REQUESTS_DIR, request_file)
            new_request_path = os.path.join(REQUESTS_DIR, f"processing_{request_file}")
            os.rename(request_path, new_request_path)  # Rename file before processing

            with open(new_request_path, 'r') as file:
                request_content = file.read().strip().split('\n')
                request_data = {line.split(': ')[0]: line.split(': ')[1] for line in request_content}

            action = request_data.get('Action')
            response = ""

            if action == 'CreateDatabase':
                database_name = request_data.get('DatabaseName')
                response = create_database(database_name)
                response_file = 'create_database_response.txt'

            elif action == 'AddFlashcard':
                database_name = request_data.get('DatabaseName')
                question = request_data.get('Question')
                answer = request_data.get('Answer')
                response = add_flashcard(database_name, question, answer)
                response_file = 'add_flashcard_response.txt'

            elif action == 'RetrieveFlashcards':
                database_name = request_data.get('DatabaseName')
                response = retrieve_flashcards(database_name)
                response_file = 'retrieve_flashcards_response.txt'

            with open(os.path.join(RESPONSES_DIR, response_file), 'w') as file:
                if isinstance(response, dict):
                    file.write(json.dumps(response, indent=2))
                else:
                    file.write(response)

            os.remove(new_request_path)  # Remove the processed file

        time.sleep(1)

if __name__ == "__main__":
    if not os.path.exists(REQUESTS_DIR):
        os.makedirs(REQUESTS_DIR)
    if not os.path.exists(RESPONSES_DIR):
        os.makedirs(RESPONSES_DIR)
    if not os.path.exists(DATABASES_DIR):
        os.makedirs(DATABASES_DIR)

    process_requests()
