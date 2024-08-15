import streamlit as st
import base64
import os

if 'history' not in st.session_state:
    st.session_state.history = []
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""

background_image_path = "hehe.jpg"
user_icon_path = "user_icon.png"
bot_icon_path = "bot_icon.png"
logo_image_path = "head.png"

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

encoded_background_image = image_to_base64(background_image_path)
encoded_user_icon = image_to_base64(user_icon_path)
encoded_bot_icon = image_to_base64(bot_icon_path)
encoded_logo_image = image_to_base64(logo_image_path)

st.markdown(f"""
    <style>
        body {{
            background-image: url("data:image/png;base64,{encoded_background_image}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        .stApp {{
            background: rgba(226, 218, 214, 0.8);
            background-size: cover;
        }}
        input[type="text"] {{
            background-color: #6377a0;
            color: #E2DAD6;
        }}
        #input-container {{
            width: 100%;
            background-color: #E2DAD6;
            box-shadow: 0px 2px 10px rgba(0,0,0,0.1);
            z-index: 1000;
            margin-bottom: 20px;
        }}
        #input-container > div {{
            width: 100%;
        }}
        .message-container {{
            display: flex;
            align-items: flex-start;
            margin-top: 10px;
            margin-bottom: 5px;
        }}
        .message-container img {{
            width: 24px;
            height: 24px;
            border-radius: 50%;
            margin: 0 4px;
        }}
        .user-msg {{
            background-color: #7FA1C3;
            color: #E2DAD6;
            padding: 8px;
            border-radius: 10px;
            max-width: 70%;
            overflow-wrap: break-word;
            display: flex;
            align-items: center;
            margin-left: auto;
            margin-right: 10px;
            position: relative;
        }}
        .user-msg .message-content {{
            text-align: right;
            margin-right: 32px;
        }}
        .user-msg img {{
            position: absolute;
            right: 0;
            margin: 0;
        }}
        .bot-msg {{
            background-color: #7FA1C3;
            color: #E2DAD6;
            padding: 8px;
            border-radius: 10px;
            max-width: 70%;
            overflow-wrap: break-word;
            margin-right: auto;
            margin-left: 10px;
            display: flex;
            align-items: center;
            position: relative;
        }}
        .bot-msg .message-content {{
            text-align: left;
            margin-left: 32px;
        }}
        .bot-msg img {{
            position: absolute;
            left: 0;
            margin: 0;
        }}
        .logo {{
            display: block;
            margin: 0 auto;
            width: 250px;
        }}
    </style>
""", unsafe_allow_html=True)

st.markdown(f"""
    <div class="logo">
        <img src="data:image/png;base64,{encoded_logo_image}" alt="Logo"/>
    </div>
""", unsafe_allow_html=True)

uploaded_file = st.sidebar.file_uploader("Upload Your Medical Report Here", type=["pdf", "docx", "txt"])

if uploaded_file is not None:
    upload_folder = "uploaded_files"
    os.makedirs(upload_folder, exist_ok=True)
    
    file_path = os.path.join(upload_folder, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getvalue())
    
    st.sidebar.success(f"File {uploaded_file.name} uploaded successfully!")

st.sidebar.title("About")
st.sidebar.info("""
    This medical chatbot is designed to provide general information and guidance. 
    It is not a substitute for professional medical advice, diagnosis, or treatment. 
    Always seek the advice of your physician or other qualified health provider 
    with any questions you may have regarding a medical condition.
""")

def handle_input():
    if st.session_state.user_input:
        response = "Thank you for your query. This is a dummy response to showcase the chatbot's interaction. In a real scenario, the chatbot's response would appear here, providing relevant medical information or advice based on the user's input."
        
        st.session_state.history.append(('You', st.session_state.user_input))
        st.session_state.history.append(('AI', response))
        
        st.session_state.user_input = ""

def get_width(length):
    base_width = 150
    scale_factor = 3
    return f"{base_width + length * scale_factor}px"

st.markdown("<div id='input-container'>", unsafe_allow_html=True)
with st.container():
    st.text_input(" ", placeholder="Enter your medical query here:", key="user_input", on_change=handle_input)
st.markdown("</div>", unsafe_allow_html=True)

for role, message in reversed(st.session_state.history):
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
