import streamlit as st
import os
from openai import OpenAI
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from fpdf import FPDF
import io
from streamlit_extras.switch_page_button import switch_page

# Store api key
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

def generate_pdf(text: str) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for line in text.split("\n"):
        pdf.multi_cell(0, 10, line)

    pdf_output = pdf.output(dest='S').encode('latin1')  # returns PDF as string, encode to bytes
    return io.BytesIO(pdf_output)

if not st.session_state.api_key:
    # Load OpenAI API key
    load_dotenv()
    # api_key = os.getenv("OPENAI_API_KEY")
    api_key = st.text_input("OpenAI API Key", type="password")
    st.session_state.api_key = api_key
client = OpenAI(api_key=st.session_state.api_key)

if not st.session_state.api_key:
    # st.error("API key not found. Make sure OPENAI_API_KEY is set in your .env file.")
    st.error("Please add your OpenAI API key to continue.", icon="🗝️")
    st.stop()

# st.set_page_config(page_title="Personalized Fitness Plan", layout="wide")
st.title("🥗 Personalized Fitness Plan")

# Store state
if "summary" not in st.session_state:
    st.session_state.summary = ""
if "fitness_plan" not in st.session_state:
    st.session_state.fitness_plan = ""

if not st.session_state.summary or st.session_state.summary is None:
    st.warning("Please generate your health summary first.")
    # if st.button("Go to Health Summary"):
        #switch_page("2_summarize_health")  # use the actual name of your health summary file without `.py`
else:

    # Show summary if exists
    if st.session_state.summary:
        st.markdown("### 📝 Health Summary")
        st.markdown(st.session_state.summary)

    # Button to generate fitness plan based on health summary
    if st.session_state.summary and st.button("🍽 Generate 1-Week Fitness Plan"):
        fitness_prompt = f"""
Generate a personalized 7-day fitness plan for a user based on the following health summary:

Health Summary:
{st.session_state.summary}

User Preferences:
- Goal: Improve energy and overall fitness
- Limitations: None reported
- Time available per day: 30–45 minutes
- Preferred activity types: Cardio, strength training, flexibility

The plan should:
- Be varied across the week
- Include rest or light activity days
- Mention specific exercises with durations
- Be safe for someone with {st.session_state.summary.lower()}.

Format the response clearly with days of the week as headings.
"""

        llm = ChatOpenAI(model="gpt-4", openai_api_key=api_key)
        fitness_response = llm.invoke(fitness_prompt)
        st.session_state.fitness_plan = fitness_response.content

    # Show fitness plan and download
    if st.session_state.fitness_plan:
        st.markdown("### 🧾 1-Week Fitness Plan")
        st.markdown(st.session_state.fitness_plan)

        # Download as txt
        st.download_button(
            label="📥 Download Fitness Plan (txt)",
            data=st.session_state.fitness_plan,
            file_name="1_week_fitness_plan.txt",
            mime="text/plain"
        )

        # Download as PDF
        pdf_buffer = generate_pdf(st.session_state.fitness_plan)
        st.download_button(
            label="📄 Download Fitness Plan (PDF)",
            data=pdf_buffer,
            file_name="1_week_fitness_plan.pdf",
            mime="application/pdf"
        )
