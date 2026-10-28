
import os
import asyncio
import json
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from backboard import BackboardClient

# Load environment variables
load_dotenv()
API_KEY = os.getenv("BACKBOARD_API_KEY")

# Page configuration
st.set_page_config(
    page_title="Ghost Notes",
    page_icon="👻",
    layout="wide"
)

# Initialize session state
# Permanent Notes Storage
NOTES_FILE = Path(__file__).resolve().parent / "notes.json"


def load_saved_notes():
    if NOTES_FILE.exists():
        try:
            with open(NOTES_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except (json.JSONDecodeError, OSError):
            return []

    return []


def save_notes_to_file(notes):
    with open(NOTES_FILE, "w", encoding="utf-8") as file:
        json.dump(notes, file, indent=4, ensure_ascii=False)


# Initialize session state
if "saved_notes" not in st.session_state:
    st.session_state.saved_notes = load_saved_notes()

if "generated_quiz" not in st.session_state:
    st.session_state.generated_quiz = ""

if "generated_quiz_data" not in st.session_state:
    st.session_state.generated_quiz_data = []

if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False

if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}

if "generated_quiz" not in st.session_state:
    st.session_state.generated_quiz = ""


# AI connection
async def get_ai_response(prompt):
    if not API_KEY:
        raise ValueError(
            "BACKBOARD_API_KEY is missing from your .env file."
        )

    async with BackboardClient(api_key=API_KEY) as client:
        response = await client.send_message(
            prompt,
            stream=False
        )

        return response.content


def ask_ai(prompt):
    return asyncio.run(get_ai_response(prompt))


# Sidebar navigation
st.sidebar.title("👻 Ghost Notes")
st.sidebar.caption("The Forgotten Knowledge Keeper")

page = st.sidebar.radio(
    "Navigate",
    [
        "🏠 Home",
        "📚 My Study Notes",
        "👻 Explain My Notes",
        "📝 Quiz Creator",
        "ℹ️ About"
    ]
)


# HOME PAGE
if page == "🏠 Home":

    st.title("👻 Ghost Notes")
    st.subheader("Your Spooky AI Study Companion 📚")

    st.write(
        "Welcome to Ghost Notes! Organize your study notes, "
        "understand difficult topics, and prepare for exams."
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("📚 **Study Notes**")
        st.write("Save and organize your learning materials.")

    with col2:
        st.info("👻 **AI Explanations**")
        st.write("Understand difficult topics in simple English.")

    with col3:
        st.info("📝 **AI Quiz Creator**")
        st.write("Generate practice questions from your notes.")

    st.divider()

    st.subheader("🚀 Start Learning")

    st.write(
        "Choose a page from the sidebar to start using "
        "your study assistant."
    )

    st.success("Built for students who dare to learn! 🎃")


# STUDY NOTES PAGE
elif page == "📚 My Study Notes":

    st.title("📚 My Study Notes")

    subject = st.text_input("Enter subject name")

    notes = st.text_area(
        "Enter your study notes",
        height=250,
        placeholder="Type or paste your study notes here..."
    )

    if st.button("💾 Save Notes"):

        if subject.strip() and notes.strip():

            st.session_state.saved_notes.append({
                "subject": subject.strip(),
                "notes": notes.strip()
            })

            try:
                save_notes_to_file(st.session_state.saved_notes)
                st.success("Your notes have been saved permanently! 💾")

            except OSError as error:
                st.error("Could not save notes to file.")
                st.caption(str(error))

        else:
            st.warning("Please enter both subject and notes.")

    st.divider()
    st.subheader("📖 Saved Notes")

    if st.session_state.saved_notes:

        for index, item in enumerate(st.session_state.saved_notes):

            with st.expander(f"📚 {item['subject']}"):

                st.write(item["notes"])

                if st.button("🗑️ Delete Note", key=f"delete_note_{index}"):

                    st.session_state.saved_notes.pop(index)

                    try:
                        save_notes_to_file(st.session_state.saved_notes)
                        st.success("Note deleted successfully!")

                    except OSError as error:
                        st.error("Could not update notes file.")
                        st.caption(str(error))

                    st.rerun()

    else:
        st.info("No notes saved yet.")

# EXPLAIN MY NOTES PAGE
elif page == "👻 Explain My Notes":

    st.title("👻 Explain My Notes")

    st.write(
        "Paste your notes and let AI explain them "
        "in a way that is easy to understand."
    )

    topic = st.text_input("Enter topic or subject")

    notes = st.text_area(
        "Paste your study notes",
        height=220,
        placeholder="Enter your notes here..."
    )

    level = st.selectbox(
        "Choose explanation style",
        [
            "Beginner-friendly",
            "Simple English",
            "Detailed explanation"
        ]
    )

    if st.button("✨ Explain My Notes"):

        if not notes.strip():

            st.warning("Please enter your study notes.")

        else:

            prompt = f"""
You are Ghost Notes, a helpful educational study assistant.

Explain these study notes using the {level} style.

Topic: {topic or "Not specified"}

Study notes:
{notes}

Use clear headings, simple language, and examples.
Stay grounded in the supplied notes.
If something is missing, explain that clearly.
"""

            with st.spinner("👻 AI is explaining your notes..."):

                try:
                    answer = ask_ai(prompt)

                    st.subheader("📖 Explanation")
                    st.markdown(answer)

                except Exception as error:

                    st.error("AI explanation failed.")
                    st.caption(str(error))


# QUIZ CREATOR PAGE
# QUIZ CREATOR PAGE
elif page == "📝 Quiz Creator":

    st.title("📝 Ghost Notes — Interactive Quiz")

    st.write(
        "Paste your study notes, generate a quiz, "
        "select your answers, and check your score!"
    )

    quiz_notes = st.text_area(
        "📚 Paste your study notes",
        height=250,
        placeholder="Paste your study notes here..."
    )

    number = st.slider(
        "Number of questions",
        min_value=3,
        max_value=10,
        value=5
    )

    if st.button("🎃 Generate Quiz"):

        if not quiz_notes.strip():
            st.warning("Please paste your study notes first.")

        else:
            prompt = f"""
You are an educational quiz creator.

Create exactly {number} multiple-choice questions
based only on the study notes below.

Return ONLY valid JSON in this format:
{{
  "questions": [
    {{
      "question": "Question text",
      "options": {{
        "A": "Option one",
        "B": "Option two",
        "C": "Option three",
        "D": "Option four"
      }},
      "answer": "A",
      "explanation": "Short explanation"
    }}
  ]
}}

Rules:
- The answer must be exactly A, B, C, or D.
- Provide exactly four options per question.
- Use simple English.
- Do not use Markdown code fences.
- Base all questions on the supplied notes.

Study notes:
{quiz_notes}
"""

            with st.spinner("👻 Creating your quiz..."):

                try:
                    import json

                    response = ask_ai(prompt)

                    # Extract JSON if the AI adds extra text
                    start = response.find("{")
                    end = response.rfind("}")

                    if start == -1 or end == -1:
                        raise ValueError(
                            "The AI did not return valid JSON. Please try again."
                        )

                    quiz_data = json.loads(response[start:end + 1])
                    questions = quiz_data.get("questions", [])

                    if not questions:
                        raise ValueError("No questions were generated.")

                    st.session_state.generated_quiz_data = questions
                    st.session_state.quiz_submitted = False
                    st.session_state.quiz_answers = {}

                    st.success(
                        f"Successfully generated {len(questions)} questions!"
                    )

                except Exception as error:
                    st.error("Quiz generation failed.")
                    st.caption(str(error))

    # Display the interactive quiz
    if st.session_state.get("generated_quiz_data"):

        questions = st.session_state.generated_quiz_data

        st.divider()
        st.subheader("👻 Answer Your Questions")

        if not st.session_state.get("quiz_submitted", False):

            with st.form("interactive_quiz_form"):

                selected_answers = {}

                for i, question in enumerate(questions):

                    st.markdown(
                        f"### Question {i + 1}: {question['question']}"
                    )

                    options = question.get("options", {})

                    choices = [
                        f"{letter}. {options.get(letter, '')}"
                        for letter in ["A", "B", "C", "D"]
                    ]

                    selected = st.radio(
                        "Choose your answer:",
                        choices,
                        index=None,
                        key=f"quiz_question_{i}"
                    )

                    selected_answers[i] = (
                        selected[0] if selected else None
                    )

                    st.divider()

                submitted = st.form_submit_button(
                    "✅ Submit My Answers"
                )

                if submitted:

                    st.session_state.quiz_answers = selected_answers
                    st.session_state.quiz_submitted = True
                    st.rerun()

        else:

            score = 0

            for i, question in enumerate(questions):

                correct = str(question.get("answer", "")).strip().upper()
                selected = st.session_state.quiz_answers.get(i)

                st.markdown(
                    f"### Question {i + 1}: {question['question']}"
                )

                if selected == correct:
                    score += 1
                    st.success("✅ Correct answer!")
                else:
                    st.error("❌ Incorrect answer.")

                options = question.get("options", {})

                st.write(
                    f"**Your answer:** "
                    f"{selected if selected else 'Not answered'}"
                )

                st.write(
                    f"**Correct answer:** {correct}. "
                    f"{options.get(correct, '')}"
                )

                st.info(
                    f"💡 Explanation: "
                    f"{question.get('explanation', 'No explanation provided.')}"
                )

                st.divider()

            percentage = round((score / len(questions)) * 100)

            st.subheader("🏆 Your Final Result")

            st.metric(
                "Your Score",
                f"{score} / {len(questions)}",
                f"{percentage}%"
            )

            if percentage >= 80:
                st.balloons()
                st.success("Excellent work, bro! 🎉")
            elif percentage >= 50:
                st.success("Good effort! Keep practising! 💪")
            else:
                st.info("Keep learning, bro. Try the quiz again! 📚")

            if st.button("🔄 Try Another Quiz"):
                st.session_state.generated_quiz_data = []
                st.session_state.quiz_submitted = False
                st.session_state.quiz_answers = {}
                st.session_state.generated_quiz = ""
                st.rerun()


# ABOUT PAGE
elif page == "ℹ️ About":

    st.title("ℹ️ About Ghost Notes")

    st.write(
        "Ghost Notes is an AI-powered study companion "
        "that helps students organize study materials, "
        "understand concepts, and practise with quizzes."
    )

    st.subheader("✨ Features")

    st.markdown("""
    - 📚 Organize study notes
    - 👻 AI-powered explanations
    - 📝 AI-generated practice quizzes
    - 🎯 Choose the number of quiz questions
    - 🔐 Store API keys in a local environment file
    """)

    st.subheader("🛠️ Technology")

    st.write(
        "Python, Streamlit, and the Backboard SDK."
    )

    st.caption("Built for students who dare to learn! 🎃")

