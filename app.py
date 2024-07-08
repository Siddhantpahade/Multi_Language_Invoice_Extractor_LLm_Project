def is_valid_prompt(prompt):
    # Check if the prompt has any word characters and is longer than a certain length
    return bool(re.search(r'\w+', prompt)) and len(prompt) > 10

# Your existing code below
from dotenv import load_dotenv

load_dotenv()  # Load all the environment variables from .env

import streamlit as st
import os
import re
from PIL import Image
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to load Gemini Pro Vision
model = genai.GenerativeModel('gemini-pro-vision')

def get_gemini_response(input, image, prompt):
    response = model.generate_content([input, image[0], prompt])
    print("Full Response:", response)  # Print the full response for debugging

    try:
        # Directly access the candidates attribute from the response object
        candidates = response.candidates
        if not candidates:
            raise ValueError("No candidates found in the response.")
        
        # Check the finish reason
        finish_reason = candidates[0].finish_reason
        if finish_reason == "SAFETY":
            raise ValueError("The response was blocked due to safety concerns.")
        
        # Assuming we want the first candidate's first part text
        content = candidates[0].content
        if not content:
            raise ValueError("No content found in the candidate.")
        
        parts = content.parts
        if not parts:
            raise ValueError("No parts found in the candidate content.")
        
        text = parts[0].text
        return text

    except (KeyError, IndexError, TypeError, AttributeError, ValueError) as e:
        print("Error navigating response structure:", e)
        print("Full response for debugging:", response)
        return str(e)

def input_image_details(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [
            {
                "mime_type": uploaded_file.type,
                'data': bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")

# Initialize our Streamlit app
st.set_page_config(page_title="Multilingual Invoice Analyzer")

st.header("Multilingual Invoice Analyzer")
input_text = st.text_input("Input Prompt: ", key="input")
uploaded_file = st.file_uploader("Choose an image of the invoice...", type=['jpg', 'jpeg', 'png'])

image = ''
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

submit = st.button("Provide details about the invoice")

input_prompt = """
You are an expert in interpreting invoices. We will upload an image of an invoice, 
and you will need to answer any questions based on the provided invoice image.
"""

# If submit button is clicked
if submit:
    if uploaded_file and is_valid_prompt(input_text):
        image_data = input_image_details(uploaded_file)
        response = get_gemini_response(input_prompt, image_data, input_text)
        st.subheader("The Response is")
        st.write(response)
    else:
        st.subheader("Error")
        st.write("Please provide a meaningful input prompt related to invoice details.")
