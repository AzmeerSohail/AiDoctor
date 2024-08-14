import streamlit as st
import base64
import zlib
from sentence_transformers import SentenceTransformer, CrossEncoder
from pinecone.grpc import PineconeGRPC as Pinecone
from groq import Groq
from dotenv import load_dotenv
import os
import re
import PyPDF2
from io import BytesIO

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
    
    def getGroqReply(self, role, model, prompt):
        messages = [
            {"role": "user", "content": prompt}
        ]
        
        chat_completion = self.client.chat.completions.create(
            messages=messages,
            model=model,
            temperature=0,
            max_tokens=1000
        )
        return chat_completion.choices[0].message.content

    def generate_response(self, conversation_history, query):
        checking_prompt = """ Check the following query and tell if it is a medical related query for a doctor chatbot or not, 
        Query: {query} 
        Just Reply "Yes" if it is and "No" if it is not a medical or related query for a doctor chatbot """
        checking_prompt = checking_prompt.format(query=query)

        message = self.getGroqReply("classifier", "llama3-8b-8192", checking_prompt)
        print("\n The Query {} according to Mixtral is {}".format(query, message))
        if re.search(message, "Yes") or re.search(message, 'yes'):
            context = self.retrieve(query)
            index = [i for i in range(len(context))]
            score = self.scores(query, context)
            res = list(zip(index, score, context))
            sorted_res = sorted(res, key=lambda x: x[1], reverse=True)
            context = [x[2] for x in sorted_res][:3]
            context = " \\n".join(context)
            history = ''
            for i in conversation_history:
                history = history + i[0] + " : " + i[1] + " \n"
            print("\n Context: {}".format(context))
            context_prompt = """Extract following details and combine them in form of a detailed information paragraph from the following context information about a disease:
             1. Names of the possible diseases mentioned
             2. Symptoms mentioned for each diseases
             3. Possible Causes mentioned for each diseases
             4. Medical Advice or Recommendations mentioned for each disease

             Context : {context}
             """
            context_prompt = context_prompt.format(context=context)
            revised_context = self.getGroqReply("Medical", "llama3-8b-8192", context_prompt)
            print("\n The Revised Context for it is: {}".format(revised_context))
            prompt_template = """
            
            Role: You are a medical AI bot tasked with providing a diagnosis based on the user's mentioned symptoms and the given disease context.

            Inputs:
            
            Question: {query}
            
            Possible Disease Context: {context}

            User Chat History: {history}
            
            Instructions:

            1. Use the provided chat history, query, and relevant medical information to formulate your response.
            2. If unsure, respond with "I don't know."
            3. Ensure the answer is both relevant and comprehensive.
            4. Keep the response concise, limited to 2-3 sentences.
            5. Answer in a conversational manner, incorporating insights from the disease context.
        """

            prompt = prompt_template.format(context=revised_context, query=query, history=history)
            assistant_message = self.getGroqReply("Medical", "llama3-8b-8192", prompt)
        else:
            prompt = ''' Based on the following chat history between an AI doctor bot and Patient reply query: {query}.
             Chat history: {history}
              Note: 
              1. You can also add information to it to create a credible answer but answer should not exceed 1-2 sentences.
              2. If the query is relevant to any medical domain or problem and has no reference relating to the chat history then
              just respond "Sorry, I am a medical AI chatbot, I only answer medical related queries"   '''
            prompt = prompt.format(query=query, history=conversation_history)
            
            assistant_message = self.getGroqReply("Medical", "llama3-8b-8192", prompt)
        print("\n Final Reply is {}".format(assistant_message))
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
def get_width(length):
    base_width = 150  # Minimum width
    scale_factor = 3  # Width increase per character
    return f"{base_width + length * scale_factor}px"
def handle_input():
    if st.session_state.user_input:
        response = rg.generate_response(st.session_state['conversation_history'], st.session_state.user_input)
        st.session_state.conversation_history.insert(0, ('AI', response))  # Insert response at the start
        st.session_state.conversation_history.insert(0, ('You', st.session_state.user_input))  # Insert query at the start
        st.session_state.user_input = ""

def handle_pdf(pdf_file):
    if pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page].extract_text()
        return text
    return ""

# User input text field with placeholder text
st.text_input(" ", placeholder="Enter your medical query here:", key="user_input", on_change=handle_input)

# File uploader for PDFs
uploaded_file = st.file_uploader("Upload a PDF document", type="pdf")

if st.button('Submit PDF'):
    if uploaded_file:
        pdf_text = handle_pdf(uploaded_file)
        if pdf_text.strip():
            prompt = f"Based on the following text extracted from a PDF document, provide a diagnosis or advice:\n\n{pdf_text}\n\nUser Chat History: {st.session_state['conversation_history']}"
            response = rg.getGroqReply("Medical", "llama3-8b-8192", prompt)
            st.session_state.conversation_history.insert(0, ('AI', response))
        else:
            st.session_state.conversation_history.insert(0, ('AI', "No text extracted from the PDF."))
    else:
        st.session_state.conversation_history.insert(0, ('AI', "No PDF file uploaded."))

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
