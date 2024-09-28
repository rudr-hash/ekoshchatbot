import streamlit as st
import subprocess
import sys

# Ensure required packages are installed
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import openai
except ImportError:
    install("openai")
    import openai

try:
    from PyPDF2 import PdfReader
except ImportError:
    install("PyPDF2")
    from PyPDF2 import PdfReader

try:
    import docx
except ImportError:
    install("python-docx")
    import docx

import io
import os
import tempfile

# Set up OpenAI API key (replace with your key or use st.secrets for better security)
openai.api_key = "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"

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "files" not in st.session_state:
    st.session_state.files = {}

def extract_text(file):
    text = ""
    if file.name.endswith('.pdf'):
        pdf_reader = PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    elif file.name.endswith('.docx'):
        doc = docx.Document(file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    return text

def save_file(file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.name)[1]) as tmp_file:
        tmp_file.write(file.getvalue())
        return tmp_file.name

def chat_with_gpt(message, context=""):
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant for a university assignment submission system. You can answer questions about assignments, provide suggestions for improvement, and discuss academic topics."},
            {"role": "user", "content": f"Context: {context}\n\nUser question: {message}"}
        ]
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages
        )
        
        return response.choices[0].message['content']
    except Exception as e:
        return f"An error occurred: {str(e)}"

def main():
    st.set_page_config(page_title="Assignment Submission Chatbot", page_icon="📚", layout="wide")
    
    st.title("📚 Assignment Submission Chatbot")
    st.markdown("Welcome to the Assignment Submission Chatbot! Upload your assignments and chat about them.")

    # Sidebar for file upload
    with st.sidebar:
        st.header("📤 File Upload")
        uploaded_file = st.file_uploader("Choose a file (PDF or DOCX)", type=['pdf', 'docx'])
        if uploaded_file is not None:
            file_text = extract_text(uploaded_file)
            file_path = save_file(uploaded_file)
            st.session_state.files[uploaded_file.name] = {"path": file_path, "text": file_text}
            st.success(f"File uploaded: {uploaded_file.name}")

        st.header("📁 Uploaded Files")
        for filename in st.session_state.files:
            st.write(filename)

    # Main chat interface
    st.header("💬 Chat")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask about your assignments..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Prepare context from uploaded files
        context = "\n\n".join([f"File: {filename}\nContent: {fileinfo['text'][:500]}..." for filename, fileinfo in st.session_state.files.items()])

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = chat_with_gpt(prompt, context)
            message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    main()
