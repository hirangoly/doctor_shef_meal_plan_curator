import streamlit as st
import os
from openai import OpenAI
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
from fpdf import FPDF
import io

# Store api key
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

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

# st.set_page_config(page_title="Health Summary", layout="wide")
st.title("🩺 Health Status Summary ")

# Store state
if "summary" not in st.session_state:
    st.session_state.summary = ""

# Expander for dropdowns
with st.expander("🔬 Select Your Health Metrics", expanded=True):
    iron_status = st.selectbox("Iron Level", ["Low", "Normal", "High", "I don't know"])
    vitamin_d_status = st.selectbox("Vitamin D Level", ["Low", "Normal", "High", "I don't know"])
    calcium_status = st.selectbox("Calcium Level", ["Low", "Normal", "High", "I don't know"])
    cholesterol_status = st.selectbox("Cholesterol Level", ["Low", "Normal", "High", "I don't know"])
    hemoglobin_status = st.selectbox("Hemoglobin Level", ["Low", "Normal", "High", "I don't know"])
    wbc_status = st.selectbox("WBC Level", ["Low", "Normal", "High", "I don't know"])
    glucose_status = st.selectbox("Glucose Level (Fasting)", ["Low", "Normal", "High", "I don't know"])
    tsh_status = st.selectbox("TSH Level", ["Low", "Normal", "High", "I don't know"])
    allergies_status = st.selectbox("Allergies", ["Yes", "No", "I don't know"])

# Button to summarize
if st.button("✅ Generate Health Summary"):
    health_status = {
        "Iron": iron_status,
        "Vitamin D": vitamin_d_status,
        "Calcium": calcium_status,
        "Cholesterol": cholesterol_status,
        "Hemoglobin": hemoglobin_status,
        "WBC": wbc_status,
        "Glucose": glucose_status,
        "TSH": tsh_status,
        "Allergies": allergies_status
    }

    prompt = f"""
    You are a medical assistant.

    Based on the following health lab statuses, summarize the patient's overall health, highlight any concerns, and recommend actions:

    {health_status}
    """

    llm = ChatOpenAI(model="gpt-4", openai_api_key=api_key)
    response = llm.invoke(prompt)
    st.session_state.summary = response.content

# Show summary if exists
if st.session_state.summary:
    st.markdown("### 📝 Health Summary")
    st.markdown(st.session_state.summary)
