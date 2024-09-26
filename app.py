import streamlit as st
import os
import subprocess
import time
from lightrag.core.generator import Generator
from lightrag.core.component import Component
from lightrag.core.model_client import ModelClient
from lightrag.components.model_client import OllamaClient

# Set up Ollama (you might need to adjust this part depending on your deployment environment)
def setup_ollama():
    os.environ['OLLAMA_HOST'] = '0.0.0.0:11434'
    os.environ['OLLAMA_ORIGINS'] = '*'
    subprocess.Popen(["ollama", "serve"])
    time.sleep(10)  # Give Ollama some time to start

# Define the SimpleQA component
class SimpleQA(Component):
    def __init__(self, model_client: ModelClient, model_kwargs: dict):
        super().__init__()
        self.generator = Generator(
            model_client=model_client,
            model_kwargs=model_kwargs,
            template=qa_template,
        )

    def call(self, query: str) -> str:
        return self.generator.call({"input_str": query})

# Define the QA template
qa_template = r"""<SYS>
You are a helpful assistant who is the backend of a prompt-based interface which simplifies CRM (Customer Relationship Management) tasks. Your tasks include creating a marketing campaign for an audience, integrating other services like email to notify, creating reports, etc. Take suitable prompts as Input.
</SYS>
User: {{input_str}}
You:"""

# Set up the Streamlit app
st.set_page_config(page_title="CRM Assistant", page_icon="🤖", layout="wide")

# Custom CSS for improved UI
st.markdown("""
<style>
    .main {
        background-color: #f5f5f5;
    }
    .stTextInput>div>div>input {
        background-color: #ffffff;
        border-radius: 10px;
        border: 1px solid #ddd;
        padding: 10px;
    }
    .stChatMessage {
        background-color: #ffffff;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    h1 {
        color: #2c3e50;
        font-family: 'Arial', sans-serif;
    }
    h2 {
        color: #34495e;
        font-family: 'Arial', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# Title and subheading
st.title("CRM Assistant")
st.subheader("Serri's own CRM Chatbot")

# Brief description
st.markdown("""
Welcome to your personal CRM assistant! I'm here to help you with various Customer Relationship Management tasks. 
Feel free to ask about creating marketing campaigns, integrating email services, generating reports, and more.
""")

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What can I help you with today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Set up Ollama and SimpleQA (only do this once)
    if 'qa' not in st.session_state:
        setup_ollama()
        model = {
            "model_client": OllamaClient(),
            "model_kwargs": {"model": "llama3.1:8b"}
        }
        st.session_state.qa = SimpleQA(**model)

    # Generate response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        assistant_response = st.session_state.qa.call(prompt)
        
        # Check if assistant_response is a string, if not, convert it to string
        if not isinstance(assistant_response, str):
            assistant_response = str(assistant_response.data)
        
        # Simulate stream of response with milliseconds delay
        for chunk in assistant_response.split():
            full_response += chunk + " "
            time.sleep(0.05)
            # Add a blinking cursor to simulate typing
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Add a button to clear the conversation
if st.button('Clear Conversation'):
    st.session_state.messages = []
    st.experimental_rerun()
