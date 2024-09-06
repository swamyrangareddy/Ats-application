import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json
import pandas as pd
import docx2txt 
import re 


load_dotenv()  # Load all environment variables

def app():
    
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    #Folder path 
    folder_path = "D:\Resuems"

    #Gemini Pro Response 
    def get_gemini_response(input_text):
        model = genai.GenerativeModel('gemini-pro')
        try: 
            response = model.generate_content(input_text)
            return response.text
        except Exception as e :
            print(f"Error processing input: {e}")
            return None 

    def input_pdf_text(uploaded_file):  
        if uploaded_file is not None:
            reader = pdf.PdfReader(uploaded_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
        else:
            raise FileNotFoundError("No file uploaded")

    def input_docx_text(uploaded_file):
        if uploaded_file is not None:
            text = docx2txt.process(uploaded_file)
            #text = ""
            #for para in doc.paragraphs:
            #    text += para.text
            return text
        else:
            raise FileNotFoundError("No file uploaded")

    # Prompt 
    input_prompt = """
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

    data = []

    # Streamlit app
    #st.radio("Select on one" ,["upload file","path"],index=0)
    st.title("Smart ATS")
    folder_path = st.text_input("Enter the folder path containing resumes")

    submit = st.button("Submit")

    if submit:
        if folder_path:
            
            # Iterate through the files in the folder
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                if filename.endswith('.pdf') or filename.endswith('.docx'):
                    try:
                        if filename.endswith('.pdf'):
                            text = input_pdf_text(file_path)
                        elif filename.endswith('.docx'):
                            text = input_docx_text(file_path)

                        formatted_prompt = input_prompt.format(text=text)
                        response = get_gemini_response(formatted_prompt)

                        # Replace single quotes with double quotes (if necessary)
                    
                        response = re.sub(r"'", '"', response)
                        response = response.replace('\n', ' ')  # Replace newlines with a space

                        # Parse the response and validate extracted data
                        parsed_data = json.dumps(response)

                        # Append the parsed data to the data list
                        data.append(parsed_data)
                    except Exception as e:
                        print(f"Error processing file {filename}: {e}")

            # Create a DataFrame and save to CSV
            df = pd.DataFrame(data)
            df.to_csv('resumes_folder_output.csv', index=True)

            st.success("your Folder data is Successfully saved to resumes_folder_output.csv")
        else:
            st.error("Please enter a valid folder path.")