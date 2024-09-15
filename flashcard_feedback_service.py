import os
import time

FEEDBACK_FILE = "feedback.txt"
REVIEWS_DIR = "databases"

# Ensure the reviews directory exists
os.makedirs(REVIEWS_DIR, exist_ok=True)

def process_feedback():
    while True:
        time.sleep(1)
        if os.path.exists(FEEDBACK_FILE):
            try:
                with open(FEEDBACK_FILE, 'r') as file:
                    content = file.read().strip()
                os.remove(FEEDBACK_FILE)  # Remove the file after reading

                if content:
                    lines = content.split('\n')
                    action = lines[0].split(":")[1].strip()
                    if action == "SubmitCategoryReview":
                        response_message = process_submit_review(lines)

                        # Write response to feedback.txt
                        with open(FEEDBACK_FILE, "w") as response_file:
                            response_file.write(response_message)

            except PermissionError:
                # Handle the error, e.g., skip this file and try again later
                continue

def process_submit_review(lines):
    database = None
    review = None

    for line in lines:
        if line.startswith("DatabaseName:"):
            database = line.split(":")[1].strip()
        
        elif line.startswith("Review:"):
            review = line.split(":")[1].strip()

    if database and review:
        filename = os.path.join(REVIEWS_DIR, f"{database.replace(' ', '_')}_reviews.txt")
        with open(filename, "a") as review_file:
            review_file.write(f"DatabaseName: {database}\nReview: {review}\n\n")
        return f"Message: Review added successfully to '{database}'."
    else:
        return "Message: Invalid review format."

if __name__ == "__main__":
    process_feedback()
