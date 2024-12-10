import streamlit as st
from crewai import Crew  # Import CrewAI
from main import run


st.title("CrewAI + Streamlit Integration")

# Input field for user to provide a topic or task
user_input = st.text_input("Enter your task or topic:")

# Button to trigger CrewAI
if st.button("Submit Task"):
    if user_input:
        # Call the CrewAI function with the input
        output = handle_task(user_input)
        # Display the output
        st.write("CrewAI Output:")
        st.write(output)
    else:
        st.warning("Please enter a task or topic!")


# app.py

def handle_task(task_input):
    """
    Handle the task input using the process_with_crew function from main.py.
    """
    try:
        result = run(task_input)  # Call the function from main.py
        return result if result else "No output from CrewAI."
    except Exception as e:
        return f"An error occurred: {str(e)}"


if __name__ == "__main__":
    st.set_page_config(page_title="CrewAI with Streamlit", layout="centered")