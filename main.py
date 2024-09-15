from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QWidget, QStackedWidget, QLineEdit, QListWidget, QInputDialog, QMessageBox,
    QListWidgetItem, QFileDialog, QFormLayout, QTextEdit, QDialog, 
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QShortcut, QKeySequence
import os
import json
import time

class CategoryWidget(QWidget):
    clicked = pyqtSignal(str)
    add_category_clicked = pyqtSignal()

    def __init__(self, category_name, delete_callback, show_add_button):
        super().__init__()
        self.category_name = category_name
        layout = QVBoxLayout()

        top_row_layout = QHBoxLayout()
        label = QLabel(category_name)
        top_row_layout.addWidget(label)

       

        delete_button = QPushButton("Delete")
        delete_button.setFixedSize(50, 30)
        delete_button.clicked.connect(lambda: delete_callback(category_name))
        top_row_layout.addWidget(delete_button)

        layout.addLayout(top_row_layout)

        if show_add_button:
            add_category_button = QPushButton("+")
            add_category_button.setFixedSize(30, 30)
            add_category_button.clicked.connect(self.emit_add_category_click)
            layout.addWidget(add_category_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)
        self.mousePressEvent = self.emit_click

    def emit_click(self, event):
        self.clicked.emit(self.category_name)

    def emit_add_category_click(self):
        self.add_category_clicked.emit()


class FeedbackWindow(QDialog):
    def __init__(self, feedback_data):
        super().__init__()
        self.setWindowTitle("Feedback")

        layout = QVBoxLayout()
        self.feedback_display = QTextEdit()
        self.feedback_display.setReadOnly(True)
        layout.addWidget(self.feedback_display)

        # Display the feedback
        self.feedback_display.setText(feedback_data)

        self.setLayout(layout)
        self.resize(400, 300)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Main Window")
        self.setGeometry(100, 100, 800, 600)

        self.categories = []
        self.current_category = None
        self.current_card = None

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        nav_layout = QHBoxLayout()

        home_button = QPushButton("Home")
        study_button = QPushButton("Study Session")

        nav_layout.addWidget(home_button)
        nav_layout.addWidget(study_button)
        main_layout.addLayout(nav_layout)

        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        # Home page
        self.home_page = QWidget()
        self.home_layout = QVBoxLayout()
        self.home_layout.addWidget(QLabel("Welcome to this study session!"))

        self.button_layout = QHBoxLayout()
        self.study_button = QPushButton("Study Session")
        self.study_button.setFixedSize(500, 600)
        self.study_button.clicked.connect(lambda: self.show_page(self.study_page))

        self.button_layout.addStretch()
        self.button_layout.addWidget(self.study_button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.button_layout.addStretch()
        self.home_layout.addLayout(self.button_layout)

        self.home_page.setLayout(self.home_layout)
        self.stacked_widget.addWidget(self.home_page)

       
        # Study session page
        self.study_page = QWidget()
        study_layout = QVBoxLayout()
        study_layout.addWidget(QLabel("Currently, only the flashcard feature has been applied. We hope you will organize your flashcards into categories for easier access and review during your study time. "))
        study_layout.addWidget(QLabel("Click the Flashcard button to get in! "))
        study_layout.addWidget(QLabel("As the flashcard page is not going to be written the instruction, because of the sidebar layout."))
        study_layout.addWidget(QLabel("Here are the instruction for using the flashcard: Click the ""+ Add Category"" button to create a new category. "))
        study_layout.addWidget(QLabel("Next, click the category that you made, click the ""+ Add card"" button, you will be able to write the front and the back of your flashcard."))
        study_layout.addWidget(QLabel("You can click back button if you suddenly don't want to make the card, or press done when you finished."))
    

        self.study_button_layout = QHBoxLayout()
        self.flashcard_button = QPushButton("Flashcard")
        self.coming_soon_button = QPushButton("Coming Soon")
        self.coming_soon_button.setEnabled(False)

        self.flashcard_button.setFixedSize(500, 600)
        self.coming_soon_button.setFixedSize(500, 600)

        self.flashcard_button.clicked.connect(lambda: self.show_page(self.flashcard_page))

        self.study_button_layout.addStretch()
        self.study_button_layout.addWidget(self.flashcard_button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.study_button_layout.addWidget(self.coming_soon_button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.study_button_layout.addStretch()
        study_layout.addLayout(self.study_button_layout)

        self.study_page.setLayout(study_layout)
        self.stacked_widget.addWidget(self.study_page)

        # Flashcard page
        self.flashcard_page = QWidget()
        flashcard_layout = QVBoxLayout()

        # Menu bar for Export, Import, and Search Flashcards
        self.menu_bar = QWidget()
        menu_layout = QHBoxLayout()
        
      
        self.menu_bar.setLayout(menu_layout)
        flashcard_layout.addWidget(self.menu_bar)

        # Sidebar for categories
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)
        flashcard_layout.addWidget(self.sidebar)

        # Main content area
        self.flashcard_main_layout = QVBoxLayout()
        self.flashcard_container = QWidget()
        self.flashcard_container.setLayout(self.flashcard_main_layout)
        flashcard_layout.addWidget(self.flashcard_container)

        # Add Category Button
        add_category_button = QPushButton("+ Add Category")
        add_category_button.clicked.connect(self.add_category)
        flashcard_layout.addWidget(add_category_button)

        self.flashcard_page.setLayout(flashcard_layout)
        self.stacked_widget.addWidget(self.flashcard_page)

        # Add/Edit card page
        self.add_card_page = QWidget()
        add_card_layout = QVBoxLayout()

        self.front_text = QLineEdit()
        self.back_text = QLineEdit()

        back_button = QPushButton("Back")
        back_button.clicked.connect(lambda: self.show_page(self.flashcard_page))

        done_button = QPushButton("Done")
        done_button.clicked.connect(self.save_card)

        add_card_layout.addWidget(QLabel("Front"))
        add_card_layout.addWidget(self.front_text)
        add_card_layout.addWidget(QLabel("Back"))
        add_card_layout.addWidget(self.back_text)

        button_row = QHBoxLayout()
        button_row.addWidget(back_button)
        button_row.addWidget(done_button)

        add_card_layout.addLayout(button_row)
        self.add_card_page.setLayout(add_card_layout)
        self.stacked_widget.addWidget(self.add_card_page)

        home_button.clicked.connect(lambda: self.show_page(self.home_page))
        study_button.clicked.connect(lambda: self.show_page(self.study_page))

        central_widget.setLayout(main_layout)

        # Shortcuts
        self.shortcut_add_category = QShortcut(QKeySequence("Ctrl+N"), self)
        self.shortcut_add_category.activated.connect(self.add_category)

        self.shortcut_add_flashcard = QShortcut(QKeySequence("Ctrl+M"), self)
        self.shortcut_add_flashcard.activated.connect(lambda: self.show_page(self.add_card_page))

        self.shortcut_toggle_flashcard = QShortcut(QKeySequence("Ctrl+T"), self)
        self.shortcut_toggle_flashcard.activated.connect(self.toggle_first_flashcard)

        self.shortcut_navigate_home = QShortcut(QKeySequence("Ctrl+H"), self)
        self.shortcut_navigate_home.activated.connect(lambda: self.show_page(self.home_page))

        self.shortcut_navigate_study = QShortcut(QKeySequence("Ctrl+S"), self)
        self.shortcut_navigate_study.activated.connect(lambda: self.show_page(self.study_page))

        self.shortcut_navigate_flashcards = QShortcut(QKeySequence("Ctrl+F"), self)
        self.shortcut_navigate_flashcards.activated.connect(lambda: self.show_page(self.flashcard_page))

    def show_page(self, page):
        self.stacked_widget.setCurrentWidget(page)
        # self.todo_button.setVisible(page == self.home_page)
        self.study_button.setVisible(page == self.home_page)

    def add_category(self):
        category_name, ok = QInputDialog.getText(self, 'New Category', 'Enter category name:')
        if ok and category_name:
            # Create the request to create a new database (category)
            request_content = (
                f"Action: CreateDatabase\n"
                f"DatabaseName: {category_name}"
            )

            # Write the request to a file
            request_file = os.path.join('requests', f'request_create_database_{time.time()}.txt')
            with open(request_file, 'w') as file:
                file.write(request_content)

            # Wait for the response from the backend (or any processing script)
            self.wait_for_response('create_database_response.txt')

            # Assuming the category creation was successful, add it to the internal categories list
            self.categories.append({"name": category_name, "cards": []})
            self.update_sidebar()
            


    def update_sidebar(self):
        self.sidebar.clear()
        for i, category in enumerate(self.categories):
            item = QListWidgetItem()
            show_add_button = i == len(self.categories) - 1
            item_widget = CategoryWidget(
                category_name=category["name"],
                # _callback=self.edit_category,edit
                delete_callback=self.delete_category,
                show_add_button=show_add_button
            )

            # Correctly pass the category name to load_category
            item_widget.clicked.connect(lambda _, name=category["name"]: self.load_category(name))
            item_widget.add_category_clicked.connect(self.add_category)

            item.setSizeHint(item_widget.sizeHint())
            self.sidebar.addItem(item)
            self.sidebar.setItemWidget(item, item_widget)

    def load_category(self, category_name):
        print(f"Loading category: {category_name}")
        self.current_category = next((c for c in self.categories if c["name"] == category_name), None)
        if self.current_category is None:
            print(f"Category '{category_name}' not found.")
        self.show_flashcards()


    def show_flashcards(self):
        if self.current_category is None:
            
            return

        # Clear the existing widgets in the layout
        for i in reversed(range(self.flashcard_main_layout.count())): 
            widget = self.flashcard_main_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # Add flashcards to the layout
        for card in self.current_category["cards"]:
            card_widget = self.create_card_widget(card)
            self.flashcard_main_layout.addWidget(card_widget)

        # Add the "+ Add Card" button
        add_card_button = QPushButton("+ Add Card")
        add_card_button.clicked.connect(lambda: self.show_page(self.add_card_page))
        self.flashcard_main_layout.addWidget(add_card_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Add the "Generate Quiz" and "Submit Review" buttons
        generate_quiz_button = QPushButton("Generate Quiz")
        generate_quiz_button.clicked.connect(self.generate_quiz)
        self.flashcard_main_layout.addWidget(generate_quiz_button, alignment=Qt.AlignmentFlag.AlignCenter)


        export_flashcards_button = QPushButton("Export Flashcard")
        export_flashcards_button.clicked.connect(self.export_flashcards)
        self.flashcard_main_layout.addWidget(export_flashcards_button, alignment=Qt.AlignmentFlag.AlignCenter)

        submit_review_button = QPushButton("Submit Review")
        submit_review_button.clicked.connect(self.submit_category_review)
        self.flashcard_main_layout.addWidget(submit_review_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Add a button to display feedback
        display_feedback_button = QPushButton("Display Feedback")
        display_feedback_button.clicked.connect(self.display_feedback)
        self.flashcard_main_layout.addWidget(display_feedback_button, alignment=Qt.AlignmentFlag.AlignCenter)


    def create_card_widget(self, card):
        card_widget = QWidget()
        card_layout = QVBoxLayout()

        card_content_layout = QVBoxLayout()
        card_button = QPushButton(card["front"])
        card_button.setFixedSize(200, 200)
        card_button.setStyleSheet("font-size: 18px;")
        card_button.clicked.connect(lambda _, b=card_button, c=card: self.toggle_card(b, c))

        button_row = QHBoxLayout()
        
        # edit_button = QPushButton("Edit")
        # edit_button.setFixedSize(50, 30)
        # edit_button.clicked.connect(lambda _, c=card: self.edit_card(c))
        # button_row.addWidget(edit_button)

        delete_button = QPushButton("Delete")
        delete_button.setFixedSize(50, 30)
        delete_button.clicked.connect(lambda _, c=card: self.confirm_delete_card(c))
        button_row.addWidget(delete_button)

        
        card_content_layout.addWidget(card_button, alignment=Qt.AlignmentFlag.AlignCenter)
        card_content_layout.addLayout(button_row)

        card_container = QWidget()
        card_container.setLayout(card_content_layout)
        card_container.setStyleSheet("border: 1px solid black;")
        
        card_layout.addWidget(card_container, alignment=Qt.AlignmentFlag.AlignCenter)
        card_widget.setLayout(card_layout)
        
        return card_widget

    # Function to display feedback in a separate window
    def display_feedback(self):
        feedback_window = QWidget()
        feedback_window.setWindowTitle("Flashcard Feedback")
        feedback_layout = QVBoxLayout()

        feedback_label = QLabel("Here is the feedback:")
        feedback_layout.addWidget(feedback_label)

        # Retrieve feedback (mockup here, replace with actual feedback retrieval)
        feedback = "Feedback: This flashcard was very helpful!"

        feedback_text = QLabel(feedback)
        feedback_layout.addWidget(feedback_text)

        feedback_window.setLayout(feedback_layout)
        feedback_window.setGeometry(200, 200, 400, 200)
        feedback_window.show()

    def toggle_card(self, button, card):
        if button.text() == card["front"]:
            button.setText(card["back"])
        else:
            button.setText(card["front"])

    def toggle_first_flashcard(self):
        """Toggle the first flashcard in the current category as an example."""
        if self.current_category and self.current_category["cards"]:
            first_card = self.current_category["cards"][0]
            first_card_button = self.flashcard_main_layout.itemAt(0).widget().findChild(QPushButton)
            if first_card_button:
                self.toggle_card(first_card_button, first_card)

    def save_card(self):
        

        new_card = {
            "front": self.front_text.text(),
            "back": self.back_text.text()
        }

        # Add the new card to the current category
        self.current_category["cards"].append(new_card)

        request_content = (
            f"Action: AddFlashcard\n"
            f"DatabaseName: {self.current_category['name']}\n"
            f"Question: {new_card['front']}\n"
            f"Answer: {new_card['back']}"
        )

        request_file = os.path.join('requests', f'request_add_flashcard_{time.time()}.txt')
        with open(request_file, 'w') as file:
            file.write(request_content)

        # Wait for the response and handle it
        self.wait_for_response('add_flashcard_response.txt')

        # After saving the card, update the UI to reflect the changes
        self.show_flashcards()
        self.show_page(self.flashcard_page)

            

    def wait_for_response(self, response_filename):
        self.response_file = os.path.join('responses', response_filename)
        self.response_timer = QTimer(self)
        self.response_timer.timeout.connect(self.check_response)
        self.response_timer.start(100) 

    def check_response(self):
        if os.path.exists(self.response_file):
            with open(self.response_file, 'r') as file:
                response_content = file.read()
                QMessageBox.information(self, 'Response', response_content)

            os.remove(self.response_file)
            self.response_timer.stop()

            if "quiz" in self.response_file:
                self.show_page(self.flashcard_page)
            else:
                self.show_flashcards()
                
    def delete_card(self):
        if self.current_card:
            self.current_category["cards"].remove(self.current_card)
            self.current_card = None
            self.show_page(self.flashcard_page)
            self.show_flashcards()

    def confirm_delete_card(self, card):
        reply = QMessageBox.question(self, 'Message', "Are you sure you want to delete this card? This action cannot be undone.", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.current_category["cards"].remove(card)
            self.show_flashcards()


    def delete_category(self, category_name):
        reply = QMessageBox.question(self, 'Message', "Are you sure you want to delete this category? This action cannot be undone.", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.categories = [c for c in self.categories if c["name"] != category_name]
            self.update_sidebar()



    
    def wait_for_export_completion(self, timeout=30):
        export_file_path = os.path.join('exports', 'export.txt')
        start_time = time.time()
        while time.time() - start_time < timeout:
            if os.path.exists(export_file_path):
                try:
                    with open(export_file_path, 'r') as file:
                        content = file.read().strip()
                    if "Message:" in content:
                        # Add a small delay before attempting to remove the file
                        time.sleep(0.5)
                        
                        # Retry deleting the file until it succeeds or times out
                        delete_start_time = time.time()
                        while time.time() - delete_start_time < 5:  # 5 seconds timeout for deletion
                            if os.path.exists(export_file_path):  # Check if the file still exists
                                try:
                                    os.remove(export_file_path)  # Clean up after reading
                                    break
                                except PermissionError:
                                    time.sleep(0.5)
                            else:
                                break
                        return content
                except PermissionError:
                    time.sleep(0.5)
                    continue
            time.sleep(1)
        return "Export timed out."



    def export_flashcards(self):
        # Set a fixed file name and path within the 'exports' directory
        export_file_name = f"{self.current_category['name']}_export.txt"
        export_file_path = os.path.join('exports', export_file_name)

        # Write the request to export.txt for the microservice
        request_content = (
            f"Action: ExportFlashcards\n"
            f"DatabaseName: {self.current_category['name']}\n"
            f"ExportFile: {export_file_name}"
        )

        # Write the request to export.txt
        with open(os.path.join('exports', 'export.txt'), 'w') as export_file_handle:
            export_file_handle.write(request_content)
        
        # Debugging: Print the request to verify content
        print(f"Request written to export.txt: {request_content}")

        # Wait for export completion
        completion_message = self.wait_for_export_completion()

        # Show the export status in a message box
        QMessageBox.information(self, "Export Status", completion_message)



    def display_feedback(self):
        if self.current_category:
            feedback_file = os.path.join('databases', f"{self.current_category['name'].replace(' ', '_')}_reviews.txt")
            if os.path.exists(feedback_file):
                with open(feedback_file, 'r') as file:
                    feedback_data = file.read()
                feedback_window = FeedbackWindow(feedback_data)
                feedback_window.exec()
            else:
                QMessageBox.information(self, "No Feedback", "No feedback available for this category.")
        


    def review_category(self, review_text, review_score):
        request_content = (
            f"Action: SubmitCategoryReview\n"
            f"DatabaseName: {self.current_category['name']}\n"
            f"Review: {review_text}\n"
            f"Score: {review_score}"
        )

        # Write the request content to feedback.txt
        with open('feedback.txt', 'w') as file:
            file.write(request_content)

        # Wait for the response from the feedback service
        self.wait_for_response('feedback.txt')

    def submit_category_review(self):
        # Ask the user to input their review
        review_text, ok = QInputDialog.getText(self, "Submit Review", "Enter your review:")
        if not ok or not review_text:
            return

        # Ask the user to input a score
        review_score, ok = QInputDialog.getInt(self, "Submit Review", "Enter a score (1-5):", 1, 1, 5)
        if not ok:
            return

        # Save the review to feedback.txt for the feedback service
        self.review_category(review_text, review_score)


    def submit_review(self):
        new_card = {
            "front": self.front_text.text(),
            "back": self.back_text.text()
        }

        # Add the new card to the current category
        self.current_category["cards"].append(new_card)

        request_content = (
            f"Action: AddFlashcard\n"
            f"DatabaseName: {self.current_category['name']}\n"
            f"Question: {new_card['front']}\n"
            f"Answer: {new_card['back']}"
        )

        request_file = os.path.join('requests', f'request_add_flashcard_{time.time()}.txt')
        with open(request_file, 'w') as file:
            file.write(request_content)

        # Wait for the response and handle it
        self.wait_for_response('add_flashcard_response.txt')

        # After saving the card, update the UI to reflect the changes
        self.show_flashcards()
        self.show_page(self.flashcard_page)
        
    def generate_quiz(self):
        # Prepare the flashcards data
        flashcards = json.dumps(self.current_category["cards"])

        # Quiz settings (e.g., number of questions)
        quiz_settings = json.dumps({
            "num_questions": min(len(self.current_category["cards"]), 5)
        })

        # Create the request for quiz generation
        request_content = (
            f"Action: GenerateQuiz\n"
            f"DatabaseName: {self.current_category['name']}\n"
            f"SelectedFlashcards: {flashcards}\n"
            f"QuizSettings: {quiz_settings}"
        )

        # Save the request in the current directory as 'quiz.txt'
        request_file = 'quiz.txt'
        try:
            with open(request_file, 'w') as file:
                file.write(request_content)
            print(f"Request saved to {request_file}")
        except Exception as e:
            print(f"Failed to save the request: {e}")
            return

        # Wait for the response from the quiz service
        response_filename = f"{self.current_category['name'].replace(' ', '_')}_quiz.txt"
        try:
            self.wait_for_response_quiz(response_filename)
        except TimeoutError as e:
            print(e)
            return

        # Display the quiz and allow user input
        response_file = os.path.join('quizs', response_filename)
        try:
            if os.path.exists(response_file):
                with open(response_file, 'r') as file:
                    quiz_content = file.read()
                    self.display_quiz(quiz_content)
        except Exception as e:
            print(f"Failed to read the response file: {e}")

    def wait_for_response_quiz(self, response_filename):
        response_file = os.path.join('quizs', response_filename)
        timeout = 30  # seconds to wait for the response
        start_time = time.time()

        print(f"Waiting for response file: {response_file}")

        while time.time() - start_time < timeout:
            if os.path.exists(response_file):
                print(f"Response file found: {response_file}")
                return True
            time.sleep(1)  # Wait 1 second before checking again

        raise TimeoutError(f"No response received for {response_filename} within the timeout period.")

    def display_quiz(self, quiz_content):
        self.quiz_window = QWidget()
        self.quiz_window.setWindowTitle("Quiz")
        quiz_layout = QVBoxLayout()

        # Parse the quiz content into individual questions
        self.quiz_questions = self.parse_quiz(quiz_content)

        # Clear user answers from any previous quiz
        self.user_answers = []

        # Display each question with a corresponding input field
        for idx, question in enumerate(self.quiz_questions):
            question_label = QLabel(f"Q{idx + 1}: {question}")
            quiz_layout.addWidget(question_label)

            answer_input = QLineEdit()
            quiz_layout.addWidget(answer_input)
            self.user_answers.append(answer_input)

        # Add a submit button
        submit_button = QPushButton("Submit Answers")
        submit_button.clicked.connect(self.submit_quiz_answers)
        quiz_layout.addWidget(submit_button)

        self.quiz_window.setLayout(quiz_layout)
        self.quiz_window.setGeometry(200, 200, 400, 300)
        self.quiz_window.show()

    def parse_quiz(self, quiz_content):
        """
        Parses the quiz content into individual questions.
        This assumes that each question is on a new line.
        """
        # Assuming each line is a new question
        questions = quiz_content.strip().splitlines()
        return questions

    def submit_quiz_answers(self):
        # Collect the user's answers
        answers = [input_field.text() for input_field in self.user_answers]
        points = self.process_answers(answers)

        # Update the results file
        results_file = os.path.join('quizs', f"{self.current_category['name'].replace(' ', '_')}_quiz.txt")
        with open(results_file, 'a') as file:
            file.write(f"Answers Submitted:\n{', '.join(answers)}\n")
            file.write(f"Total Points: {points}\n")

        # Show a message box with the points and reference to the results file
        QMessageBox.information(self.quiz_window, "Quiz Completed", f"Your total points: {points}\nRefer to '{results_file}' for details.")

        # Close the quiz window after showing the message box
        self.quiz_window.close()

    def process_answers(self, answers):
        # Here you should process the answers against the actual questions
        # For simplicity, let's assume each correct answer gives 1 point
        total_points = 0

        # Example of basic answer checking (this should be tailored to your actual needs)
        correct_answers = [card['back'] for card in self.current_category["cards"]]

        for correct_answer, user_answer in zip(correct_answers, answers):
            if correct_answer.strip().lower() == user_answer.strip().lower():
                total_points += 1

        return total_points
    
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()



