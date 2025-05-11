import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from fpdf import FPDF

# Store api key
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

if not st.session_state.api_key:
    # Load OpenAI API key
    load_dotenv()
    # api_key = os.getenv("OPENAI_API_KEY")
    api_key = st.text_input("OpenAI API Key", type="password")
    st.session_state.api_key = api_key

# Create OpenAI client
client = OpenAI(api_key=st.session_state.api_key)

if "recipe_card" not in st.session_state:
    st.session_state.recipe_card = ""

def generate_pdf(text: str) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    # pdf.set_font("Arial", size=12)

    # Use a valid Unicode font path
    font_path = "/Library/Fonts/Arial Unicode.ttf"  # Adjust if needed
    pdf.add_font("ArialUnicode", "", font_path, uni=True)
    pdf.set_font("ArialUnicode", size=12)

    for line in text.split("\n"):
        pdf.multi_cell(0, 10, line)

    pdf_output = pdf.output(dest='S').encode('latin1')  # returns PDF as string, encode to bytes
    return io.BytesIO(pdf_output)


def generate_recipe_card(recipe_name):
    prompt = f"""
    Create a detailed recipe card in Markdown format for "{recipe_name}".
    Include:
    - Title
    - Short description
    - Prep time, cook time, servings
    - Ingredients (as a list)
    - Instructions (step-by-step)
    - Add emojis where appropriate
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content

# Streamlit UI
# st.set_page_config(page_title="Generate Recipe")
st.title("🍲 Generate Recipe")

recipe_name = st.text_input("Enter a recipe name", placeholder="e.g., Spicy Chickpea Curry")

if st.button("Generate Recipe"):
    if recipe_name.strip():
        with st.spinner("Cooking up your recipe..."):
            recipe_card = generate_recipe_card(recipe_name)
            st.session_state.recipe_card = recipe_card
            # st.markdown(st.session_state.recipe_card)
    else:
        st.warning("Please enter a recipe name.")


# Show recipe card and download
if st.session_state.recipe_card:
    st.markdown("### 🧾 Recipe card - {recipe_name}")
    st.markdown(st.session_state.recipe_card)

    # Download as txt
    st.download_button(
        label="📥 Download Recipe card (txt)",
        data=st.session_state.recipe_card,
        file_name="recipe_card_{recipe_name}.txt",
        mime="text/plain"
    )

    # Download as PDF
    # pdf_buffer = generate_pdf(st.session_state.recipe_card)
    # st.download_button(
    #     label="📄 Download Recipe card (PDF)",
    #     data=pdf_buffer,
    #     file_name="recipe_card_{recipe_name}.pdf",
    #     mime="application/pdf"
    # )
