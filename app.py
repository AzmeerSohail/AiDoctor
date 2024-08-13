import streamlit as st
import base64
import os

# Initialize session state if not already done
if 'history' not in st.session_state:
    st.session_state.history = []
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""

# Paths to the images
background_image_path = "hehe.jpg"
user_icon_path = "user_icon.png"
bot_icon_path = "bot_icon.png"
logo_image_path = "head.png"  # Path to the logo image

# Convert images to base64 strings
def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

encoded_background_image = image_to_base64(background_image_path)
encoded_user_icon = image_to_base64(user_icon_path)
encoded_bot_icon = image_to_base64(bot_icon_path)
encoded_logo_image = image_to_base64(logo_image_path)

# Add custom CSS to apply the background image and icons
st.markdown(f"""
    <style>
        body {{
            background-image: url("data:image/png;base64,{encoded_background_image}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        .stApp {{
            background: rgba(226, 218, 214, 0.8); /* Semi-transparent background to improve readability */
            background-size: cover;
        }}
        input[type="text"] {{
            background-color: #6377a0; /* Input box background color */
            color: #E2DAD6; /* Input box text color */
        }}
        #input-container {{
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: #E2DAD6; /* Input container background */
            padding: 10px;
            box-shadow: 0px -2px 10px rgba(0,0,0,0.1);
            z-index: 1000; /* Ensure it stays on top of other elements */
        }}
        #input-container > div {{
            width: 100%;
        }}
        .message-container {{
            display: flex;
            align-items: flex-start; /* Align items to the start */
            margin-top: 10px; /* Space above each message */
            margin-bottom: 5px;
        }}
        .message-container img {{
            width: 24px; /* Adjust the icon size */
            height: 24px; /* Adjust the icon size */
            border-radius: 50%; /* Make the icon circular */
            margin: 0 4px; /* Adjust margin around the icon */
        }}
        .user-msg {{
            background-color: #7FA1C3;
            color: #E2DAD6;
            padding: 8px; /* Reduced padding */
            border-radius: 10px;
            max-width: 70%;
            overflow-wrap: break-word;
            display: flex;
            align-items: center;
            margin-left: auto;
            margin-right: 10px; /* Ensure there's space for the icon */
            position: relative;
            order: 1; /* Ensure the message is placed before the icon */
        }}
        .bot-msg {{
            background-color: #7FA1C3;
            color: #E2DAD6;
            padding: 8px; /* Reduced padding */
            border-radius: 10px;
            max-width: 70%;
            overflow-wrap: break-word;
            margin-right: auto;
            display: flex;
            align-items: center;
            margin-left: 10px; /* Ensure there's space for the icon */
            position: relative;
            order: 2; /* Ensure the message is placed before the icon */
        }}
        .user-msg img {{
            order: 2; /* Ensure icon is placed after the message */
        }}
        .bot-msg img {{
            order: 1; /* Ensure icon is placed before the message */
        }}
        .user-msg .message-content {{
            margin-right: 0; /* No extra space for the icon */
            text-align: right;
        }}
        .bot-msg .message-content {{
            margin-left: 0; /* No extra space for the icon */
            text-align: left;
        }}
        .logo {{
            display: block;
            margin: 0 auto;
            padding: 10px 0; /* Space above and below the logo */
            width: 250px; /* Adjust width as needed */
        }}
    </style>
""", unsafe_allow_html=True)

# Display the logo image at the top center
st.markdown(f"""
    <div class="logo">
        <img src="data:image/png;base64,{encoded_logo_image}" alt="Logo"/>
    </div>
""", unsafe_allow_html=True)


# File uploader in the sidebar
uploaded_file = st.sidebar.file_uploader("Upload Your Medical Report Here", type=["pdf", "docx", "txt"])

# Handle file saving
if uploaded_file is not None:
    upload_folder = "uploaded_files"
    os.makedirs(upload_folder, exist_ok=True)
    
    file_path = os.path.join(upload_folder, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getvalue())
    
    st.sidebar.success(f"File {uploaded_file.name} uploaded successfully!")
# Sidebar with additional information and file uploader
st.sidebar.title("About")
st.sidebar.info("""
    This medical chatbot is designed to provide general information and guidance. 
    It is not a substitute for professional medical advice, diagnosis, or treatment. 
    Always seek the advice of your physician or other qualified health provider 
    with any questions you may have regarding a medical condition.
""")



# User input handling function
def handle_input():
    if st.session_state.user_input:
        # Dummy response for demonstration
        response = "Thank you for your query. This is a dummy response to showcase the chatbot's interaction. In a real scenario, the chatbot's response would appear here, providing relevant medical information or advice based on the user's input."
        
        # Append the user's query first and then the bot response to the history
        st.session_state.history.append(('You', st.session_state.user_input))
        st.session_state.history.append(('AI', response))
        
        # Clear the input box
        st.session_state.user_input = ""

# Function to determine the width based on text length
def get_width(length):
    base_width = 150  # Minimum width
    scale_factor = 3  # Width increase per character
    return f"{base_width + length * scale_factor}px"

# Display the chat history with icons
for role, message in st.session_state.history:
    width = get_width(len(message))
    if role == 'You':
        st.markdown(f"""
            <div class='message-container'>
                <div class='message-content user-msg' style='width: {width};'>
                    {message}
                </div>
                <img src="data:image/png;base64,{encoded_user_icon}" alt="User Icon"/>
            </div>
        """, unsafe_allow_html=True)
    elif role == 'AI':
        st.markdown(f"""
            <div class='message-container'>
                <img src="data:image/png;base64,{encoded_bot_icon}" alt="Bot Icon"/>
                <div class='message-content bot-msg' style='width: {width};'>
                    {message}
                </div>
            </div>
        """, unsafe_allow_html=True)

# Place the input box at the bottom and fixed to the screen
st.markdown("<div id='input-container'>", unsafe_allow_html=True)
with st.container():
    st.text_input(" ", placeholder="Enter your medical query here:", key="user_input", on_change=handle_input)
st.markdown("</div>", unsafe_allow_html=True)
