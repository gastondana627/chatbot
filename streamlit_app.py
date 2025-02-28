import google.generativeai as genai
import streamlit as st
import re

# This MUST be the first command in the file
st.set_page_config(page_title="Teacher Chatbot", layout="wide")

# Configure Google API from Streamlit secrets
try:
    GOOGLE_API_KEY = st.secrets["google"]["api_key"]  # Read API key from secrets.toml

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

# Teacher data with courses, weeks taught, and hours per session
teacher_data = {
    "name": "Jane Doe",
    "hours_taught": 120,
    "courses_taught": ["Math 101", "Science 202", "History 303"],
    "papers_graded": 200,
    "semester_data": {
        "Math 101": {
            "fall_2024": {"weeks_taught": 12, "hours_per_week": 6, "days": ["Monday", "Wednesday", "Friday"]},
            "spring_2024": {"weeks_taught": 10, "hours_per_week": 4, "days": ["Tuesday", "Thursday"]}
        },
        "Science 202": {
            "fall_2024": {"weeks_taught": 12, "hours_per_week": 6, "days": ["Monday", "Wednesday", "Friday"]}
        },
        "History 303": {
            "fall_2024": {"weeks_taught": 12, "hours_per_week": 6, "days": ["Monday", "Wednesday", "Friday"]}
        }
    },
    "current_schedule": {
        "Monday": "Math 101 (9:00-11:00 AM)",
        "Wednesday": "Science 202 (10:00-12:00 PM)",
        "Friday": "History 303 (1:00-3:00 PM)"
    }
}

# Function to handle chatbot response
def chatbot_response(prompt):
    prompt_lower = prompt.lower()
    print(f"[DEBUG] Received prompt: {prompt_lower}")

    # Local Data: Regex for detecting how many hours taught for a specific course
    match_hours = re.search(r"(?:how many|what is the total|can you tell me the|how much) (?:hours|time) (?:were taught|did the instructor teach|was spent teaching|instruction time was given) (?:in|for|of)? ?([a-z\s\d]+)", prompt_lower)

    if match_hours:
        course = match_hours.group(1).strip()
        total_hours = 0
        semesters = teacher_data['semester_data'].get(course.title(), {})

        if semesters:
            for semester, data in semesters.items():
                total_hours += data.get("weeks_taught", 0) * data.get("hours_per_week", 0)
            return f"Jane Doe has taught {total_hours} hours in {course}."
        else:
            return f"No data available for {course}."

    # What courses does Jane Doe teach?
    elif "what courses does jane doe teach" in prompt_lower:
        courses = ", ".join(teacher_data["courses_taught"])
        return f"Jane Doe teaches the following courses: {courses}"

    # What is Jane Doe's schedule? (making the prompt more flexible)
    elif re.search(r"(what|can you tell me) (is|are) jane doe['’]s? (schedule|class|timetable)", prompt_lower):
        schedule = "\n".join([f"**{day}:** {course}" for day, course in teacher_data["current_schedule"].items()])
        return f"Here is Jane Doe's weekly schedule:\n\n{schedule}"

    else:
        return "I'm sorry, I don't have the answer."


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
user_input = st.text_input("Enter your question:", placeholder="E.g., How many hours have I taught in Math 101?")
submit_button = st.button("Send")

if submit_button and user_input:
    with st.spinner("Thinking..."):
        response = chatbot_response(user_input)
        st.success("Response:")
        st.write(response)

st.subheader("🌟 Feedback")
feedback = st.text_area("Share your feedback about the chatbot!")
if st.button("Submit Feedback"):
    st.success("Thank you for your feedback!")
