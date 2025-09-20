import streamlit as st
import PyPDF2
import io
import os
from openai import OpenAI
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="PDF Summarizer", page_icon="📚", layout="centered")

st.title("AI Resume Critiquer")
st.markdown(
    "Upload your resume in PDF format, and the AI will provide feedback on how to improve it."
)

# Default API keys from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# User-provided API keys
st.sidebar.header("🔑 API Key Settings")
user_openai_key = st.sidebar.text_input("Enter your OpenAI API Key (optional)", type="password")
user_groq_key = st.sidebar.text_input("Enter your Groq API Key (optional)", type="password")

# Use user key if provided, else fallback to .env key
OPENAI_API_KEY = user_openai_key if user_openai_key else OPENAI_API_KEY
GROQ_API_KEY = user_groq_key if user_groq_key else GROQ_API_KEY

# upload file
upload_file = st.file_uploader("Upload your resume (PDF or TXT format)", type=["pdf", "txt"])

# define the job roles
job_role = st.text_input(
    "Enter the job role you are applying for (e.g., Software Engineer, Data Scientist):",
    placeholder="Software Engineer",
)

# check if file is uploaded
analyze = st.button("Analyze Resume")

# utilities function to read files
def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
    return uploaded_file.read().decode("utf-8")

if analyze and upload_file:
    try:
        file_content = extract_text_from_file(upload_file)

        if not file_content.strip():
            st.error("The uploaded file is empty or could not be read.")
            st.stop()
        
        prompt = f"""Please analyze this resume and provide constructive feedback.
        Focus on the following aspects:
        1. Content Clarity and Impact.
        2. Skills Presentation.
        3. Experience description.
        4. Specific improvements for the job role: {job_role if job_role else "General Job application"}

        Resume Content:
        {file_content}

        Please provide your analysis in a clear, structured format with specific recommendations.
        """

        if GROQ_API_KEY:
            # Use Groq API
            client = Groq(api_key=GROQ_API_KEY)
            response = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[
                    {"role": "system", "content": "You are an expert resume reviewer with years of experience in HR and recruitment."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_completion_tokens=1024
            )
            feedback = response.choices[0].message.content.strip()
        elif OPENAI_API_KEY:
            # Use OpenAI API
            client = OpenAI(api_key=OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert resume reviewer with years of experience in HR and recruitment."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            feedback = response.choices[0].message["content"].strip()
        else:
            st.error("❌ No API key provided. Please enter your OpenAI or Groq API key in the sidebar.")
            st.stop()

        st.markdown("### AI Feedback:")
        st.write(feedback)
    
    except Exception as e:
        st.error(f"An Error occurred: {e}")
        st.stop()