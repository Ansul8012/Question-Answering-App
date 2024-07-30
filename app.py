import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from PIL import Image
import speech_recognition as sr
from gtts import gTTS
import pytesseract
import base64 
import io

# Set page configuration as the first Streamlit command
st.set_page_config(page_title="Q & A Application", page_icon=":books:", layout="centered")

# Function to add background image from local file
def add_bg_from_local(image_file):
    try:
        with open(image_file, "rb") as f:
            data = f.read()
        encoded_image = base64.b64encode(data).decode() 
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{encoded_image}");
                background-size: cover;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    except FileNotFoundError:
        st.error("Background image file not found. Please check the file path and try again.")

# Call this function at the beginning of your script
add_bg_from_local('Machine-Learning copy.jpg')  # Replace with the path to your background image

# Load environment variables from the .env file
load_dotenv()

# Configure the Google Gemini AI model with the API key from environment variables
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to load the Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")

def get_gemini_response(input_text, image_text=None):
    try:
        if image_text:
            response = model.generate_content([input_text, image_text])
        else:
            response = model.generate_content(input_text)
        
        if response.candidates and hasattr(response.candidates[0], 'content') and hasattr(response.candidates[0].content, 'parts'):
            content = ' '.join(part.text for part in response.candidates[0].content.parts)
            return content
        
        if response.candidates and hasattr(response.candidates[0], 'safety_ratings'):
            st.warning("The response was blocked due to safety concerns.")
            return "The response was blocked due to safety concerns."
        
        return "No valid response was generated."
    except ValueError as e:
        st.error(f"An error occurred: {e}")
        return "An error occurred while generating the response."

def get_speech_audio(text):
    try:
        tts = gTTS(text)
        audio_fp = io.BytesIO()
        tts.save(audio_fp)
        audio_fp.seek(0)
        return audio_fp.read()
    except Exception as e:
        st.error(f"Error in text-to-speech conversion: {e}")
        return None

recognizer = sr.Recognizer()

def get_voice_input():
    with sr.Microphone() as source:
        st.write("Listening...")
        audio = recognizer.listen(source)
        try:
            query = recognizer.recognize_google(audio)
            st.write(f"Recognized: {query}")
            return query
        except sr.UnknownValueError:
            st.write("Could not understand the audio")
        except sr.RequestError:
            st.write("Could not request results; check your network connection")

if "page" not in st.session_state:
    st.session_state.page = "landing"

def show_landing_page():
    st.title("Welcome to the Q&A Application")
    st.markdown("Choose an option below to proceed:")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Ask a Question", key="ask_text"):
            st.session_state.page = "text_input"
            st.experimental_rerun()
    with col2:
        if st.button("Ask a Question from Image", key="ask_image"):
            st.session_state.page = "image_input"
            st.experimental_rerun()

def show_text_input_page():
    st.markdown("<style>.back-button { position: absolute; top: 10px; left: 10px; }</style>", unsafe_allow_html=True)
    if st.button("Back", key='back_text'):
        st.session_state.page = "landing"
        st.experimental_rerun()

    st.markdown(
        """
        <div style="text-align:center;">
            <h1 style="color:white;">QUESTION ANSWERING SYSTEM 📚</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.markdown("<h3 style='text-align: center;'>ABOUT THE DEVELOPER</h3>", unsafe_allow_html=True)
    
    # Improved error handling for loading the image
    image_path = "Ansul copy.jpg"  # Use a relative path if the image is within the project directory
    if os.path.exists(image_path):
        st.sidebar.image(image_path, width=150, caption="Ansul Singh", use_column_width='always')
    else:
        st.sidebar.error(f"Developer image file not found at {image_path}. Please check the file path.")
        
    st.sidebar.info("I am Ansul Singh, currently pursuing my B.Tech in Computer Science and Engineering at Graphic Era Deemed to be University. As a third-year student, I have developed a strong foundation in various aspects of software development and artificial intelligence. I am passionate about creating innovative applications that can make a difference. This Question Answering System is one of my projects aimed at leveraging AI to enhance the learning experience. Get Connected with me EMAIL - ansulsingh171@gmail.com 📧")

    input_text = st.text_input("Enter your question:", key="input")
    submit_text = st.button("Ask Question")
    submit_voice = st.button("Ask Question by Voice")

    if submit_voice:
        input_text = get_voice_input()

    if submit_text or submit_voice:
        if input_text:
            response = get_gemini_response(input_text)
            st.session_state.response = response
            st.subheader("Response:")
            st.write(response)
            if st.button("Hear Response"):
                audio_bytes = get_speech_audio(response)
                if audio_bytes:
                    st.audio(audio_bytes, format='audio/mp3')

    if "history" not in st.session_state:
        st.session_state.history = []

    if (submit_text or submit_voice) and input_text:
        st.session_state.history.append({"question": input_text, "response": st.session_state.response})

    if "show_history" not in st.session_state:
        st.session_state.show_history = False

    if st.checkbox("Show Question History", value=st.session_state.show_history):
        st.session_state.show_history = True
    else:
        st.session_state.show_history = False

    if st.session_state.show_history:
        st.subheader("Question History")
        for i, entry in enumerate(st.session_state.history):
            st.write(f"**Q{i + 1}:** {entry['question']}")
            st.write(f"**A{i + 1}:** {entry['response']}")
            st.write("---")

def show_image_input_page():
    st.markdown("<style>.back-button { position: absolute; top: 10px; left: 10px; }</style>", unsafe_allow_html=True)
    if st.button("Back", key='back_image'):
        st.session_state.page = "landing"
        st.experimental_rerun()

    st.markdown(
        """
        <div style="text-align:center;">
            <h1 style="color:white;">QUESTION ANSWERING SYSTEM 📚</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.markdown("<h3 style='text-align: center;'>ABOUT THE DEVELOPER</h3>", unsafe_allow_html=True)
    
    # Improved error handling for loading the image
    image_path = "Ansul copy.jpg"  # Use a relative path if the image is within the project directory
    if os.path.exists(image_path):
        st.sidebar.image(image_path, width=150, caption="Ansul Singh", use_column_width='always')
    else:
        st.sidebar.error(f"Developer image file not found at {image_path}. Please check the file path.")
        
    st.sidebar.info("I am Ansul Singh, currently pursuing my B.Tech in Computer Science and Engineering at Graphic Era Deemed to be University. As a third-year student, I have developed a strong foundation in various aspects of software development and artificial intelligence. I am passionate about creating innovative applications that can make a difference. This Question Answering System is one of my projects aimed at leveraging AI to enhance the learning experience. Get Connected with me EMAIL - ansulsingh171@gmail.com 📧")

    uploaded_image = st.file_uploader("Upload an image containing text:", type=["jpg", "jpeg", "png"])
    if uploaded_image is not None:
        image = Image.open(uploaded_image)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        extracted_text = pytesseract.image_to_string(image)
        st.session_state.extracted_text = extracted_text

    if "extracted_text" in st.session_state:
        st.subheader("Ask a question about the image:")
        image_question = st.text_input("Enter your question:", key="image_input")
        submit_image_question = st.button("Ask Question from Image")

        if submit_image_question and image_question:
            response = get_gemini_response(image_question, st.session_state.extracted_text)
            st.session_state.image_response = response
            st.subheader("Response:")
            st.write(response)
            if st.button("Hear Response from Image Question"):
                audio_bytes = get_speech_audio(response)
                if audio_bytes:
                    st.audio(audio_bytes, format='audio/mp3')

if st.session_state.page == "landing":
    show_landing_page()
elif st.session_state.page == "text_input":
    show_text_input_page()
elif st.session_state.page == "image_input":
    show_image_input_page()
