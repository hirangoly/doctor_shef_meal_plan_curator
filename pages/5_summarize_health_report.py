import os
import fitz  # PyMuPDF
import streamlit as st
from openai import OpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from dotenv import load_dotenv

# Store api key
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

if not st.session_state.api_key:
    # Load OpenAI API key
    load_dotenv()
    # api_key = os.getenv("OPENAI_API_KEY")
    api_key = st.text_input("OpenAI API Key", type="password")
    st.session_state.api_key = api_key

if not st.session_state.api_key:
    # st.error("API key not found. Make sure OPENAI_API_KEY is set in your .env file.")
    st.error("Please add your OpenAI API key to continue.", icon="🗝️")
    st.stop()

# Store state
if "report_summary" not in st.session_state:
    st.session_state.report_summary = ""

def summarize_report(report_summary):
  prompt = f"""
    You are a medical assistant.

    Based on the following health lab statuses, summarize the patient's overall health, highlight any concerns, and recommend actions:

    {report_summary}
    """

  llm = ChatOpenAI(model="gpt-4", openai_api_key=st.session_state.api_key)
  response = llm.invoke(prompt)
  st.session_state.report_summary = response.content

def extract_text_from_pdf(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def ask_metric(qa_chain, retriever, question):
    response = qa_chain.invoke({"query": question})
    return response["result"]

def summarize_health(vectorstore):
    llm = ChatOpenAI(model="gpt-4", openai_api_key=st.session_state.api_key)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

    metrics_questions = {
        "Ferritin": "What is the Ferritin or Serum Iron level?",
        "Vitamin D": "What is the Vitamin D level (25-hydroxyvitamin D)?",
        "Cholesterol_Total": "What is the Total Cholesterol level?",
        "Cholesterol_LDL": "What is the LDL cholesterol level?",
        "Cholesterol_HDL": "What is the HDL cholesterol level?",
        "Triglycerides": "What is the Triglycerides level?",
        "Glucose": "What is the Glucose level (fasting or random)?",
        "Calcium": "What is the Calcium level?",
        "Hemoglobin": "What is the Hemoglobin level?",
        "WBC": "What is the White Blood Cell count (WBC)?",
        "TSH": "What is the TSH (Thyroid Stimulating Hormone) level?",
        "Allergies": "Are there any allergies mentioned in the report?"
    }

    results = {}
    for key, question in metrics_questions.items():
        results[key] = ask_metric(qa_chain, retriever, question)

    return results

def summarize_health_single_LLM(vectorstore):
    prompt = """
You are a medical AI assistant analyzing a patient's health report.

Your task is to extract specific lab metrics from the text, even if expressed using synonyms or in non-standard formats. Match labels carefully and provide values **with units** if found. If a metric is not mentioned, respond with `"No data"`.

Look for and return the following values in valid JSON format:

{
  "Ferritin (or Serum Iron)": "value + unit or 'No data'",
  "Vitamin D (25-hydroxyvitamin D or 25(OH)D)": "value + unit or 'No data'",
  "Cholesterol": {
    "Total": "value + unit or 'No data'",
    "LDL": "value + unit or 'No data'",
    "HDL": "value + unit or 'No data'",
    "Triglycerides": "value + unit or 'No data'"
  },
  "Glucose (Fasting or Random)": "value + unit or 'No data'",
  "Calcium": "value + unit or 'No data'",
  "Hemoglobin": "value + unit or 'No data'",
  "WBC (White Blood Cell count)": "value + unit or 'No data'",
  "TSH (Thyroid Stimulating Hormone)": "value + unit or 'No data'",
  "Allergies Noted": "text or 'No data'"
}

Do not fabricate or infer values. Only extract exact values mentioned in the report text. Be strict with accuracy.
"""

    # Set up RetrievalQA chain
    llm = ChatOpenAI(model="gpt-4", openai_api_key=st.session_state.api_key)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
        return_source_documents=True
    )

    # Run query
    # question = "Summarize all the key findings in this health report"
    # response = qa_chain.run(prompt)
    response = qa_chain.invoke({"query": prompt})

    return response["result"]

def text_into_vector(raw_text):
    # Split text into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=50)
    chunks = splitter.split_text(raw_text)

    # Vectorize chunks
    embeddings = OpenAIEmbeddings(openai_api_key=st.session_state.api_key)
    vectorstore = FAISS.from_texts(chunks, embedding=embeddings)

    return vectorstore

# Streamlit UI
st.title("🩺 AI Health Report Summarizer")
uploaded_file = st.file_uploader("Upload your health report (PDF)", type=["pdf"])

if uploaded_file:
    with st.spinner("Extracting and summarizing..."):
        extracted_text = extract_text_from_pdf(uploaded_file)
        vector_store = text_into_vector(extracted_text)
        summary = summarize_health(vector_store)
        st.subheader("📝 Factual Summary")
        st.markdown(summary)

        # summarizing using LLM
        summarize_report(summary)
        st.subheader("📝 Health Summary")
        st.markdown(st.session_state.report_summary)

