import google.generativeai as genai
import streamlit as st
import re
import json
import requests
from collections import Counter

# This MUST be the first command in the file
st.set_page_config(page_title="Teacher Chatbot", layout="wide")

# Configure Google API from Streamlit secrets
try:
    GOOGLE_API_KEY = st.secrets["google"]["api_key"]
    FORMSPREE_URL = st.secrets["formspree"]["url"]  # Formspree endpoint

    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY is missing in secrets.toml.")

    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-pro')

except ValueError as e:
    st.error(f"Error: {e}")
    st.stop()
except Exception as e:
    st.error(f"Error initializing the Gemini model: {e}")
    st.stop()

# Teacher data
teacher_data = {
    "name": "Jane Doe",
    "hours_taught": 120,
    "courses_taught": ["Math 101", "Science 202", "History 303"],
    "papers_graded": 200,
    "current_schedule": {
        "Monday": "Math 101 (9:00-11:00 AM)",
        "Wednesday": "Science 202 (10:00-12:00 PM)",
        "Friday": "History 303 (1:00-3:00 PM)"
    }
}

# Initialize session state for analytics
if "question_log" not in st.session_state:
    st.session_state["question_log"] = []

# Function to handle chatbot response
def chatbot_response(prompt):
    prompt_lower = prompt.lower()
    st.session_state["question_log"].append(prompt_lower)  # Log the question

    # Example Response
    if "courses" in prompt_lower:
        return f"Jane Doe teaches: {', '.join(teacher_data['courses_taught'])}"
    else:
        return "I'm sorry, I don't have the answer."

# Function to send feedback via Formspree
def send_feedback(email, feedback_text):
    try:
        response = requests.post(FORMSPREE_URL, json={"email": email, "message": feedback_text})

        if response.status_code == 200:
            return True
        else:
            st.error("Error submitting feedback. Please try again.")
            return False
    except Exception as e:
        st.error(f"Error sending feedback: {e}")
        return False

# Streamlit UI
st.title("📚 Teacher Management Chatbot")
st.write("Ask the chatbot about your teaching stats, schedule, or anything related to your work!")

st.sidebar.header("📊 Teacher Data Overview")
st.sidebar.write(f"**Name:** {teacher_data['name']}")
st.sidebar.write(f"**Hours Taught:** {teacher_data['hours_taught']} hours")
st.sidebar.write(f"**Courses Taught:** {', '.join(teacher_data['courses_taught'])}")
st.sidebar.write(f"**Papers Graded:** {teacher_data['papers_graded']}")

st.sidebar.subheader("📅 Weekly Schedule")
for day, schedule in teacher_data['current_schedule'].items():
    st.sidebar.write(f"**{day}:** {schedule}")

st.subheader("💬 Chat with the Assistant")
user_input = st.text_input("Enter your question:", placeholder="E.g., What courses does Jane Doe teach?")
submit_button = st.button("Send")

if submit_button and user_input:
    with st.spinner("Thinking..."):
        response = chatbot_response(user_input)
        st.success("Response:")
        st.write(response)

# **Natural Language Analytics Dashboard**
st.subheader("📊 Most Asked Questions")

if st.session_state["question_log"]:
    top_questions = Counter(st.session_state["question_log"]).most_common(5)
    st.write("Here are the most frequently asked questions:")
    for question, count in top_questions:
        st.write(f"🔹 **{question}** ({count} times)")

# Feedback Submission
st.subheader("🌟 Feedback")
user_email = st.text_input("Your Email:", placeholder="Enter your email here")
feedback_text = st.text_area("Share your feedback about the chatbot!")

if st.button("Submit Feedback"):
    if user_email and feedback_text:
        if send_feedback(user_email, feedback_text):
            st.success("Thank you! Your feedback has been sent.")
        else:
            st.error("Failed to send feedback. Please try again.")
    else:
        st.warning("Please enter both your email and feedback before submitting.")






