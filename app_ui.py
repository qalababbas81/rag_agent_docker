import streamlit as st
import requests
import json

st.set_page_config(page_title="Enterprise AI Agent", page_icon="🤖")
st.title("🤖 Enterprise Knowledge Agent")

# Sidebar for User Configuration
with st.sidebar:
    user_id = st.text_input("User ID", value="john")
    st.info("This Agent connects to MS SQL and your Document Store.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Ask me anything..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in real-time
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        # Prepare payload for your FastAPI endpoint
        payload = {"user_id": user_id, "question": prompt}
        
        # Request streaming from FastAPI
        try:
            # with requests.post("http://localhost:8000/ask-stream", 
            #                    json=payload, 
            #                    stream=True) as r:
             with requests.post("http://app:8000/ask-stream", 
                               json=payload, 
                               stream=True) as r:
                for chunk in r.iter_content(chunk_size=None, decode_unicode=True):
                    if chunk:
                        full_response += chunk
                        # Update the UI with the latest text
                        response_placeholder.markdown(full_response + "▌")
                
                # Final update without the cursor
                response_placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"Connection Error: {e}")
            full_response = "I'm having trouble reaching the server."

    # Add assistant response to history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
