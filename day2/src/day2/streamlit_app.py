import streamlit as st
from main import run

def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []

def format_response(response):
    if response is None:
        return ""
    
    if isinstance(response, tuple):
        response = response[1]
    
    # Convert the response to string if it isn't already
    response = str(response)
    
    # Clean up the string - remove literal \n and replace with actual line breaks
    response = response.replace('\\n', '\n')  # Convert literal \n to actual line breaks
    response = response.replace('/n', '\n')   # Handle potential /n
    response = response.replace('<br>', '\n') # Remove any HTML breaks
    
    # Format for streamlit display
    return response

def main():
    st.title("AI Agent Chat Interface")
    
    init_session_state()

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            content = format_response(message["content"])
            st.text(content)  # Using st.text to preserve formatting

    if prompt := st.chat_input("What would you like to discuss?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.text(prompt)

        # Create a placeholder for streaming updates
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # Run the agent system with streaming updates
            with st.spinner("Processing..."):
                try:
                    result = run()  # Get the result from run()
                    if result is not None:
                        if isinstance(result, (list, tuple)):
                            for update in result:
                                formatted_update = format_response(update)
                                full_response += formatted_update + "\n"
                                message_placeholder.text(full_response)
                        else:
                            formatted_update = format_response(result)
                            full_response = formatted_update
                            message_placeholder.text(full_response)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
            
            if full_response:  # Only append if we got a response
                st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    main() 