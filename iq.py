import streamlit as st
import requests
import time
from datetime import datetime

def fetch_questions(category="17", difficulty="medium", amount=10):
    """Fetch physics questions from Open Trivia Database."""
    url = f"https://opentdb.com/api.php?amount={amount}&category={category}&difficulty={difficulty}&type=multiple"
    response = requests.get(url)
    data = response.json()
    
    # Handle errors or different response formats
    if 'results' not in data:
        st.error("Failed to fetch questions. Please try again.")
        return []

    if data['response_code'] != 0:
        st.error("Error in fetching data. Response code: {}".format(data['response_code']))
        return []

    questions = []
    for item in data['results']:
        question_text = item['question']
        choices = item['incorrect_answers'] + [item['correct_answer']]
        correct_answer = item['correct_answer']
        questions.append({
            "question": question_text,
            "choices": choices,
            "answer": correct_answer
        })
    return questions

# Initialize session state variables
if 'session' not in st.session_state:
    st.session_state.session = 1
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'points' not in st.session_state:
    st.session_state.points = 0
if 'quiz_over' not in st.session_state:
    st.session_state.quiz_over = False
if 'questions' not in st.session_state:
    st.session_state.questions = fetch_questions(amount=10)  # Fetch initial 10 questions
if 'start_time' not in st.session_state:
    st.session_state.start_time = time.time()  # Track start time for the session
if 'answered_questions' not in st.session_state:
    st.session_state.answered_questions = 0  # Track the number of answered questions

def start_quiz():
    """Start a new quiz session."""
    st.session_state.session = 1
    st.session_state.current_question = 0
    st.session_state.points = 0
    st.session_state.quiz_over = False
    st.session_state.questions = fetch_questions(amount=10)  # Fetch questions for the new session
    st.session_state.start_time = time.time()  # Reset start time for the new session
    st.session_state.answered_questions = 0  # Reset answered questions

def next_session():
    """Move to the next session."""
    st.session_state.session += 1
    st.session_state.current_question = 0
    st.session_state.points = 0
    st.session_state.quiz_over = False
    st.session_state.questions = fetch_questions(amount=10)  # Fetch questions for the new session
    st.session_state.start_time = time.time()  # Reset start time for the new session
    st.session_state.answered_questions = 0  # Reset answered questions

def handle_answer(choice):
    """Handle answer submission and update the state."""
    question_data = st.session_state.questions[st.session_state.current_question]
    if choice == question_data['answer']:
        st.session_state.points += 10  # Each question is worth 10 points
        st.markdown('<div style="background-color: white; color: green; padding: 10px; border-radius: 5px; font-size: 16px;">Correct! You get 10 points.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="background-color: white; color: red; padding: 10px; border-radius: 5px; font-size: 16px;">Incorrect! The correct answer was: {}</div>'.format(question_data['answer']), unsafe_allow_html=True)

    # Increment answered questions count
    st.session_state.answered_questions += 1

    # Move to the next question or end the session
    if st.session_state.current_question < len(st.session_state.questions) - 1:
        st.session_state.current_question += 1
    else:
        st.session_state.quiz_over = True

def display_timer():
    """Display a countdown timer for the current session with custom styling at the bottom."""
    elapsed_time = time.time() - st.session_state.start_time
    remaining_time = max(0, 180 - int(elapsed_time))  # 180 seconds = 3 minutes
    minutes, seconds = divmod(remaining_time, 60)
    
    # Calculate marks obtained and total marks attempted
    marks_obtained = st.session_state.points
    total_marks_attempted = st.session_state.answered_questions * 10

    # Styling the timer and question count
    timer_html = f"""
    <div style="position: fixed; bottom: 0; left: 0; width: 100%; color: red; background-color: yellow; padding: 10px; border-radius: 5px; font-size: 20px; text-align: center;">
        Time remaining: {minutes:02}:{seconds:02} | Question Attempting: {st.session_state.current_question + 1}/{len(st.session_state.questions)} | Session: {st.session_state.session} | Marks Obtained: {marks_obtained} | Marks Attempted: {total_marks_attempted}
    </div>
    """
    st.markdown(timer_html, unsafe_allow_html=True)

# Display current question
if not st.session_state.quiz_over:
    # Display timer
    display_timer()
    
    elapsed_time = time.time() - st.session_state.start_time
    if elapsed_time >= 180:  # Time limit exceeded
        st.session_state.quiz_over = True
        st.error("Time's up! The session is over.")
    else:
        question_data = st.session_state.questions[st.session_state.current_question]
        
        # Custom styling for the date and time
        date_time_html = f"""
        <div style="position: relative; background-color: pink; color: black; padding: 5px; border-radius: 5px; font-size: 12px; text-align: right;">
            {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        </div>
        """
        
        # Custom styling for the question
        question_html = f"""
        <div style="background-color: pink; color: black; padding: 20px; border-radius: 5px; font-size: 18px; text-transform: uppercase;">
            {date_time_html}
            {question_data['question']}
        </div>
        """
        st.markdown(question_html, unsafe_allow_html=True)
        
        choice = st.radio("Select your answer:", question_data["choices"], key="choices")

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Submit Answer"):
                st.session_state.choice = choice
                handle_answer(choice)

        with col2:
            if st.button("Next Question") and st.session_state.current_question < len(st.session_state.questions) - 1:
                st.session_state.current_question += 1

else:
    # Styled completion message with yellow background and black font color
    result_html = f"""
    <div style="background-color: yellow; color: black; padding: 20px; border-radius: 5px; font-size: 20px;">
        Session {st.session_state.session} completed! Your score: {st.session_state.points} out of {len(st.session_state.questions) * 10}
    </div>
    """
    st.markdown(result_html, unsafe_allow_html=True)

    if st.session_state.session < 5:
        if st.button("Start Next Session"):
            next_session()
    else:
        st.write("You've completed all sessions!")

    if st.session_state.session == 5 and st.button("Restart Quiz"):
        start_quiz()
