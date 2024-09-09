import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json
import pandas as pd
import docx2txt 
import re

load_dotenv()

def app():

    # Load all environment variables

    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    def get_gemini_response(input, pdf_content, prompt):
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content([input, pdf_content[0], prompt])
        return response.text 

    def input_pdf_text(uploaded_file):
        if uploaded_file is not None:
            reader = pdf.PdfReader(uploaded_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
        else:
            raise FileNotFoundError("No file uploaded")

    def input_doc_text(uploaded_file):
        if uploaded_file is not None:
            text = docx2txt.process(uploaded_file)
            return text 
        else:
            raise FileNotFoundError("No file uploaded")
        
    def save_to_csv(data, filename="resume_output.csv"):
        df = pd.DataFrame([data])  # Convert the data to a DataFrame
        if os.path.exists(filename):
            df.to_csv(filename, mode='a', header=False, index=False)  # Append to existing file
        else:
            df.to_csv(filename, mode='w', header=True, index=False)

    ## Streamlit App 
    st.header("Smart ATS")
    input_text = st.text_area("Job Description: ", key="input")
    uploaded_file = st.file_uploader("Upload your resume (PDF/DOCX)...", type=["pdf", "docx"])

    if uploaded_file is not None:
        st.write("File Uploaded Successfully")

    submit1 = st.button("Tell Me About the Resume")
    submit2 = st.button("Percentage Match")
    submit3 = st.button("Getting Detailes")

    input_prompt1 = """
    You are an experienced Technical Human Resource Manager. Your task is to review the provided resume against the job description. 
    Please share your professional evaluation on whether the candidate's profile aligns with the role. 
    Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
    """

    input_prompt2 = """
    You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality. 
    Your task is to evaluate the resume against the provided job description. 
    Give me the percentage of match if the resume matches the job description. 
    First, the output should come as percentage, then keywords missing, and finally final thoughts.
    """

    input_prompt3=""""Given the following resume text, extract the details for the following fields: Name, Phone Number, Email ID, 
    Job Titles, Skills, Current Company, and Location If any of these details are not available in the text, return 'null' for that field.
    Provide the extracted information in a structured JSON format. 
    """
    data = []

    if submit1:
        if uploaded_file is not None:
            if uploaded_file.name.endswith('.pdf'):
                pdf_content = input_pdf_text(uploaded_file)
                response = get_gemini_response(input_prompt1, pdf_content,input_text)
            elif uploaded_file.name.endswith('.docx'):
                doc_content = input_doc_text(uploaded_file)
                response = get_gemini_response(input_prompt1, [doc_content],input_text)
            st.subheader("The Response is:")
            st.write(response)
        else:
            st.write("Please upload the resume")

    elif submit2:
        if uploaded_file is not None:
            if uploaded_file.name.endswith('.pdf'):
                pdf_content = input_pdf_text(uploaded_file)
                response = get_gemini_response(input_prompt2, pdf_content, input_text)
            elif uploaded_file.name.endswith('.docx'):
                doc_content = input_doc_text(uploaded_file)
                response = get_gemini_response(input_prompt2, [doc_content], input_text)
            st.subheader("The Response is:")
            st.write(response)
        else:
            st.write("Please upload the resume")
    elif submit3:
        if uploaded_file is not None:
            if uploaded_file.name.endswith('.pdf'):
                pdf_content = input_pdf_text(uploaded_file)
                response = get_gemini_response(input_prompt3, [pdf_content],input_text)
            elif uploaded_file.name.endswith('.docx'):
                doc_content = input_doc_text(uploaded_file)
                response = get_gemini_response(input_prompt3, [doc_content],input_text)
                st.subheader("The Response is:")
            # Replace newlines with a space
            response = re.sub(r"'", '"', response)
            response = response.replace('\n', ' ')
            st.write(response)
            response_dict = json.dumps(response)
            save_to_csv(response_dict, filename="resume_output.csv")
            
        else:
            st.write("Please upload the resume")
        
