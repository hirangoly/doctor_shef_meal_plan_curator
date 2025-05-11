import streamlit as st
import os
from openai import OpenAI
from langchain.chat_models import ChatOpenAI
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

# Load OpenAI API key
load_dotenv()
# api_key = os.getenv("OPENAI_API_KEY")
api_key = st.text_input("OpenAI API Key", type="password")
st.session_state.api_key = api_key
client = OpenAI(api_key=api_key)

if not st.session_state.api_key:
    # st.error("API key not found. Make sure OPENAI_API_KEY is set in your .env file.")
    st.error("Please add your OpenAI API key to continue.", icon="🗝️")
    st.stop()

# st.set_page_config(page_title="Personalized Meal Plan", layout="wide")
st.title("🥗 Personalized Meal Plan")

# Store state
if "summary" not in st.session_state:
    st.session_state.summary = ""
if "meal_plan" not in st.session_state:
    st.session_state.meal_plan = ""

if not st.session_state.summary or st.session_state.summary is None:
    st.warning("Please generate your health summary first.")
    # if st.button("Go to Health Summary"):
        #switch_page("2_summarize_health")  # use the actual name of your health summary file without `.py`
else:

    # Show summary if exists
    if st.session_state.summary:
        st.markdown("### 📝 Health Summary")
        st.markdown(st.session_state.summary)

    # Button to generate meal plan based on health summary
    if st.session_state.summary and st.button("🍽 Generate 2-Week Meal Plan"):
        meal_prompt = f"""
        You are a certified dietitian.

        Based on this health summary:

        {st.session_state.summary}

        Create a vegetarian 2-week Indian-style meal plan that:
        - Addresses any deficiencies (like iron, vitamin D, etc.)
        - Avoids problematic foods (e.g., if cholesterol is high)
        - Focuses on balanced, fiber-rich, nutrient-dense meals.
        """

        llm = ChatOpenAI(model="gpt-4", openai_api_key=api_key)
        meal_response = llm.invoke(meal_prompt)
        st.session_state.meal_plan = meal_response.content

    # Show meal plan and download
    if st.session_state.meal_plan:
        st.markdown("### 🧾 2-Week Meal Plan")
        st.markdown(st.session_state.meal_plan)

        # Download as txt
        st.download_button(
            label="📥 Download Meal Plan",
            data=st.session_state.meal_plan,
            file_name="2_week_meal_plan.txt",
            mime="text/plain"
        )

        # Download as PDF
        pdf_buffer = generate_pdf(st.session_state.meal_plan)
        st.download_button(
            label="📄 Download Meal Plan (PDF)",
            data=pdf_buffer,
            file_name="2_week_meal_plan.pdf",
            mime="application/pdf"
        )
