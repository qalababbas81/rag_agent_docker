import streamlit as st
import requests
import json
import pandas as pd

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
        is_sql_response = False
        # Request streaming from FastAPI
        try:
            # with requests.post("http://localhost:8000/ask-stream", 
            #                    json=payload, 
            #                    stream=True) as r:
             with requests.post("http://app:8000/ask-stream", 
                               json=payload, 
                               stream=True) as r:
                # for chunk in r.iter_lines(decode_unicode=True):
                #     if chunk:
                #         full_response += chunk
                #         # Update the UI with the latest text
                #         response_placeholder.text(full_response + "▌")
                
                # # Final update without the cursor
                # response_placeholder.text(full_response)
                for chunk in r.iter_lines(decode_unicode=True):
                    if chunk:
                        #full_response += chunk
                        full_response += chunk + "\n"
                        #response_placeholder.text(full_response + "▌")
                        response_placeholder.text("Generating response...")

                # FINAL OUTPUT (AFTER STREAM ENDS)
                is_sql_response = full_response.strip().startswith("### 📊 Database Results")

                if not is_sql_response:
                    response_placeholder.text(full_response)
                else:
                    response_placeholder.empty()
                # -------------------------
                # SQL TABLE RENDER (FIXED)
                # -------------------------
                if is_sql_response:
                    print('fdfdffffffffffffffffffffffffffffffffffffffffff')
                    st.markdown("### 📊 Database Results")

                    lines = full_response.split("\n")

                    data = []

                    for line in lines:
                        if "|" in line:
                            clean = line.replace("- ", "")
                            parts = [x.strip() for x in clean.split("|")]

                            if len(parts) == 4:
                                data.append(parts)

                    if data:
                        df = pd.DataFrame(
                            data,
                            columns=["ID", "Name", "Email", "Address"]
                        )

                        st.dataframe(df)
                
        except Exception as e:
            st.error(f"Connection Error: {e}")
            full_response = "I'm having trouble reaching the server."
        
        # try:
        #     # Note: stream=False is safer if your FastAPI isn't using StreamingResponse/yield
        #     with requests.post("http://app:8000/ask-stream", 
        #                        json=payload) as r:
                
        #         if r.status_code == 200:
        #             # 1. Parse the full JSON response
        #             data = r.json()
                    
        #             # 2. Extract the actual text from the 'answer' key
        #             # This works for both SQL (Direct Return) and Document (LLM) paths
        #             full_response = data.get("answer", "No response content found.")
                    
        #             # 3. (Optional) Simulate a typing effect for the UI
        #             # import time
        #             # displayed_text = ""
        #             # for char in full_response:
        #             #     displayed_text += char
        #             #     response_placeholder.markdown(displayed_text + "▌")
        #             #     time.sleep(0.005) # Very fast typing effect
                    
        #             # Final update without the cursor
        #             response_placeholder.markdown(full_response)
        #         else:
        #             st.error(f"Server Error: {r.status_code}")
                    
        # except Exception as e:
        #     st.error(f"Connection Error: {e}")
        #     full_response = "I'm having trouble reaching the server."

    # Add assistant response to history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
