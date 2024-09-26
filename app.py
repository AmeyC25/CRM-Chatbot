import streamlit as st
import time
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

# Load model and tokenizer
@st.cache_resource
def load_model():
    tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-chat-hf")
    model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-chat-hf")
    return tokenizer, model

tokenizer, model = load_model()

# Create a text-generation pipeline
generator = pipeline("text-generation", model=model, tokenizer=tokenizer)

# Define the QA template
qa_template = r"""<s>[INST] <<SYS>>
You are a helpful assistant who is the backend of a prompt-based interface which simplifies CRM (Customer Relationship Management) tasks. Your tasks include creating a marketing campaign for an audience, integrating other services like email to notify, creating reports, etc. Take suitable prompts as Input.
<</SYS>>

{input_str} [/INST]"""

# Define the SimpleQA function
def simple_qa(query: str) -> str:
    prompt = qa_template.format(input_str=query)
    response = generator(prompt, max_length=500, num_return_sequences=1)
    return response[0]['generated_text'].split('[/INST]')[-1].strip()

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

    # Generate response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        assistant_response = simple_qa(prompt)
        
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
