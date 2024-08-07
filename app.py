import streamlit as st
import os

# Initialize session state if not already done
if 'history' not in st.session_state:
    st.session_state.history = []
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""

# Add custom CSS to change the background color of the whole page, input box, and file uploader
st.markdown("""
    <style>
        body {
            background-color: #E2DAD6; /* Main background color */
        }
        .stApp {
            background-color: #E2DAD6; /* Ensure background color is applied to the app container */
        }
        input[type="text"] {
            background-color: #455575; /* Input box background color */
            color: #E2DAD6; /* Input box text color */
        }
        /* Style the file uploader */
        div[data-testid="stFileUploader"] > label {
            color: #152f63; /* Change the label color */
            font-size: 40px; /* Change the font size */
            font-family: Arial, sans-serif; /* Change the font family */
            font-weight: bold; /* Make the font bold */
        }
    </style>
""", unsafe_allow_html=True)

# Title of the app with custom style
st.markdown("<h1 style='text-align: center; color: #152f63;'>AI DOCTOR</h1>", unsafe_allow_html=True)

# Sidebar with additional information
st.sidebar.title("About")
st.sidebar.info("""
    This medical chatbot is designed to provide general information and guidance. 
    It is not a substitute for professional medical advice, diagnosis, or treatment. 
    Always seek the advice of your physician or other qualified health provider 
    with any questions you may have regarding a medical condition.
""")

# Function to handle file upload
def handle_file_upload(uploaded_file):
    save_directory = "uploads"  # Specify your desired directory
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)
    file_path = os.path.join(save_directory, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"File saved successfully: {file_path}")

# File uploader
uploaded_file = st.file_uploader("Upload your medical report", type=["pdf", "jpg", "jpeg", "png"])
if uploaded_file is not None:
    handle_file_upload(uploaded_file)

# User input
def handle_input():
    if st.session_state.user_input:
        # Load the chatbot model (commented out)
        #@st.cache(allow_output_mutation=True)
        #def load_model():
            # Load the model here
            # This is a placeholder; replace it with your actual model loading code
            #model = joblib.load('path_to_your_model.pkl')
            #return model

        # Load the model (commented out)
        #model = load_model()

        # Generate response (commented out)
        #response = model.predict([st.session_state.user_input])  # Adjust this line to match your model's prediction method
        
        # Dummy response for demonstration
        response = "Thank you for your query. This is a dummy response to showcase the chatbot's interaction. In a real scenario, the chatbot's response would appear here, providing relevant medical information or advice based on the user's input."
        
        # Append the user's query and bot response to the history in the correct order
        st.session_state.history.insert(0, ('AI', response))  # Insert response at the start
        st.session_state.history.insert(0, ('You', st.session_state.user_input))  # Insert query at the start
        
        # Clear the input box
        st.session_state.user_input = ""

# User input text field with placeholder text
st.text_input(" ", placeholder="Enter your medical query here:", key="user_input", on_change=handle_input)

# Function to determine the width based on text length
def get_width(length):
    # Adjust the base width and scaling factor as needed
    base_width = 150  # Minimum width
    scale_factor = 3  # Width increase per character
    return f"{base_width + length * scale_factor}px"

# Display the chat history with the most recent conversation on top
st.markdown("<h3 style='color: #152f63;'>Chat History</h3>", unsafe_allow_html=True)
for role, message in st.session_state.history:
    width = get_width(len(message))
    if role == 'You':
        st.markdown(f"<div style='background-color: #7FA1C3; color: #E2DAD6; padding: 10px; margin-bottom: 5px; border-radius: 10px; max-width: 70%; width: {width}; overflow-wrap: break-word; align-self: flex-end; text-align: right; margin-left: auto;'>{message}</div>", unsafe_allow_html=True)
    elif role == 'AI':
        st.markdown(f"<div style='background-color: #7FA1C3; color: #E2DAD6; padding: 10px; margin-bottom: 5px; border-radius: 10px; max-width: 70%; width: {width}; overflow-wrap: break-word; align-self: flex-start; text-align: left; margin-right: auto;'>{message}</div>", unsafe_allow_html=True)

# Footer with additional info
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Made by Fusion Flare Technologies</p>", unsafe_allow_html=True)