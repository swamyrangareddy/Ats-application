import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json
import pandas as pd
import docx2txt
import re
import time

load_dotenv()

def app():

    # Load all environment variables
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    def get_gemini_response(input_text, file_content, prompt):
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content([input_text, file_content, prompt])
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
        df = pd.DataFrame(data)  # Convert the data to a DataFrame
        if os.path.exists(filename):
            df.to_csv(filename, mode='a', header=False, index=False)  # Append to existing file
        else:
            df.to_csv(filename, mode='w', header=True, index=False)

    # Streamlit App
    st.header("Smart ATS")
    input_text = st.text_area("Job Description: ", key="input")
    uploaded_file = st.file_uploader("Upload your resume (PDF/DOCX)...", type=["pdf", "docx"])

    if uploaded_file is not None:
        st.write("File Uploaded Successfully")

    submit2 = st.button("Get Percentage")
    submit1 = st.button("Submit")

    input_prompt1 = """
    "Act as a highly skilled and experienced Application Tracking System (ATS) with deep expertise in the technology field, including software engineering, data science, data analysis, and big data engineering. Your task is to extract the following details from the provided resume:

    - Name
    - Phone Number
    - Email ID
    - Job Title
    - Current Company
    - Skills
    - Location

    Resume: {text}

    Please provide the response as a single string formatted as follows:
    Name: [value or 'Null'],
    Phone Number: [value or 'Null'],
    Email ID: [value or 'Null'],
    Job Title: [value or 'Null'],
    Current Company: [value or 'Null'],
    Skills: [list of values or 'Null'],
    Location: [value or 'Null']

    If any detail is not present in the resume, return 'Null' for that field."
    """

    input_prompt2 = """
    You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality. 
    Your task is to evaluate the resume against the provided job description. 
    Give me the percentage of match if the resume matches the job description. 
    First, the output should come as percentage, then keywords missing, and finally final thoughts.
    """

    if submit1:
        if uploaded_file is not None:
            if uploaded_file.name.endswith('.pdf'):
                text = input_pdf_text(uploaded_file)
                progress_bar = st.progress(0)
                progress_text = st.empty()
                
                for percent_complete in range(100):
                    time.sleep(0.05)  # Simulate processing time
                    progress_bar.progress(percent_complete + 1)
                    progress_text.text(f"Processing {uploaded_file.name}: {percent_complete + 1}% completed")
                file_content = input_pdf_text(uploaded_file)
                response = get_gemini_response(input_text, file_content, input_prompt1)
            elif uploaded_file.name.endswith('.docx'):
                text = input_doc_text(uploaded_file)
                progress_bar = st.progress(0)
                progress_text = st.empty()
                
                for percent_complete in range(100):
                    time.sleep(0.05)  # Simulate processing time
                    progress_bar.progress(percent_complete + 1)
                    progress_text.text(f"Processing {uploaded_file.name}: {percent_complete + 1}% completed")
                file_content = input_doc_text(uploaded_file)
                response = get_gemini_response(input_text, file_content, input_prompt1)

            st.subheader("The Response is:")
            response = re.sub(r"'", '"', response)  # Replace single quotes with double quotes
            response = response.replace('\n', ' ')  # Replace newlines with a space
            #st.write("Raw Response:", response)  # Debug print
            
            # Extract data using regex
            name = re.search(r"Name:\s*(.*?)(,|$)", response)
            phone = re.search(r"Phone Number:\s*(.*?)(,|$)", response)
            email = re.search(r"Email ID:\s*(.*?)(,|$)", response)
            job_title = re.search(r"Job Title:\s*(.*?)(,|$)", response)
            current_company = re.search(r"Current Company:\s*(.*?)(,|$)", response)
            skills_match = re.search(r"Skills:\s*\[(.*?)\](,|$)", response)
            location = re.search(r"Location:\s*(.*?)(,|$)", response)

            # Prepare data dictionary
            data = {
                'Name': name.group(1).strip() if name else 'Null',
                'Phone Number': phone.group(1).strip() if phone else 'Null',
                'Email ID': email.group(1).strip() if email else 'Null',
                'Job Title': job_title.group(1).strip() if job_title else 'Null',
                'Current Company': current_company.group(1).strip() if current_company else 'Null',
                'Skills': skills_match.group(1).strip() if skills_match else 'Null',
                'Location': location.group(1).strip() if location else 'Null'
            }
            
            # Create a DataFrame with a single row
            df = pd.DataFrame([data])  # Convert the data to a DataFrame with a single row
            st.write(df[['Name','Phone Number','Email ID','Job Title']])  # Display the DataFrame
            save_to_csv([data], filename="resume_output.csv")  # Pass data as a list
            
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
# Run the app
if __name__ == "__main__":
    app()
