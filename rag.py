import streamlit as st
import base64
import zlib
from sentence_transformers import SentenceTransformer, CrossEncoder
from pinecone.grpc import PineconeGRPC as Pinecone
from groq import Groq
from dotenv import load_dotenv
import os
load_dotenv()

class RAGPipeline:
    def __init__(self, pinecone_api_key, pinecone_index_name, groq_api_key):
        self.pc = Pinecone(api_key=pinecone_api_key)
        self.index = self.pc.Index(pinecone_index_name)
        self.model_emb = SentenceTransformer("neuml/pubmedbert-base-embeddings")
        self.cross_encoder = CrossEncoder('cross-encoder/ms-marco-TinyBERT-L-2-v2', max_length=512, device='cpu')
        self.client = Groq(api_key=groq_api_key)

    def decode_and_decompress_metadata(self, encoded_metadata):
        compressed_metadata = base64.b64decode(encoded_metadata)
        metadata = zlib.decompress(compressed_metadata).decode('utf-8')
        return metadata

    def retrieve(self, text, top_k=1):
        embedding = self.model_emb.encode(text).tolist()
        query_response = self.index.query(vector=embedding, top_k=25, include_metadata=True, include_values=True)
        results = [self.decode_and_decompress_metadata(match['metadata']['patient_doctor_dialogue']) for match in query_response['matches']]
        return results

    def scores(self, query, docs):
        response = [[query, doc_text] for doc_text in docs]
        score = self.cross_encoder.predict(response)
        return score

    def generate_response(self, conversation_history, query):
        context = self.retrieve(query)
        index = [i for i in range(len(context))]
        score = self.scores(query, context)
        res = list(zip(index, score, context))
        sorted_res = sorted(res, key=lambda x: x[1], reverse=True)
        context = [x[2] for x in sorted_res][:5]
        context = " \\n".join(context)
        history = ''
        for i in conversation_history:
            history = history+i[0]+" : "+i[1]+" \n"

        prompt_template = """You are a doctor bot. Provide a diagnosis based on the user's mentioned symptoms.
        Following are the Chat History between medical ai bot (you) and patient, second is the currect query mentioned as "Question", and the 
        third is the Context that is basically some reference to another case of similar symptoms, these cases are completely different from the
        current case, so just take inference from the context but do not mention the details of those cases.

        Chat History: {history}

        Question: {query}

        Context: {context}

        Instruction:
        1. Stay strictly within the provided context, query, and relevant medical information. 
        2. If unsure, respond with "I don't know."
        3. The answer should be relevant, comprehensive.
        4. Response should not exceed 2-3 sentences.

        Answer: Based on the provided information, the possible diagnosis is:"""

        prompt = prompt_template.format(context=context, query=query,history=history)

        messages = [{"role": "user", "content": prompt}]
        
        chat_completion = self.client.chat.completions.create(
            messages=messages,
            model="llama3-8b-8192",
            temperature=0,
            max_tokens=1000
        )

        assistant_message = chat_completion.choices[0].message.content
        return assistant_message
    
rg = RAGPipeline(
            pinecone_api_key=os.getenv('pinecone_api'),
            pinecone_index_name=os.getenv('pinecone_index'),
            groq_api_key=os.getenv('groq_api')
        )

# Initialize session state if not already done
if 'conversation_history' not in st.session_state:
    st.session_state['conversation_history'] = []

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

def handle_input():
    if st.session_state.user_input:

        # Generate response (commented out)
        response = rg.generate_response(st.session_state['conversation_history'], st.session_state.user_input)  # Adjust this line to match your model's prediction method
        
        # Dummy response for demonstration
        # response = "Thank you for your query. This is a dummy response to showcase the chatbot's interaction. In a real scenario, the chatbot's response would appear here, providing relevant medical information or advice based on the user's input."
        
        # Append the user's query and bot response to the history in the correct order
        st.session_state.conversation_history.insert(0, ('AI', response))  # Insert response at the start
        st.session_state.conversation_history.insert(0, ('You', st.session_state.user_input))  # Insert query at the start
        
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
for role, message in st.session_state.conversation_history:
    width = get_width(len(message))
    if role == 'You':
        st.markdown(f"<div style='background-color: #7FA1C3; color: #E2DAD6; padding: 10px; margin-bottom: 5px; border-radius: 10px; max-width: 70%; width: {width}; overflow-wrap: break-word; align-self: flex-end; text-align: right; margin-left: auto;'>{message}</div>", unsafe_allow_html=True)
    elif role == 'AI':
        st.markdown(f"<div style='background-color: #7FA1C3; color: #E2DAD6; padding: 10px; margin-bottom: 5px; border-radius: 10px; max-width: 70%; width: {width}; overflow-wrap: break-word; align-self: flex-start; text-align: left; margin-right: auto;'>{message}</div>", unsafe_allow_html=True)

# Footer with additional info
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Made by Fusion Flare Technologies</p>", unsafe_allow_html=True)

