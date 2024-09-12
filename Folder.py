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

load_dotenv()  # Load all environment variables

def app():
    
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    # Folder path
    folder_path = "D:/Resumes"

    # Gemini Pro Response
    def get_gemini_response(input_text):
        model = genai.GenerativeModel('gemini-pro')
        try:
            response = model.generate_content(input_text)
            return response.text
        except Exception as e:
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

    # List to store the extracted data
    data = []

    # Streamlit app
    st.title("Smart ATS")
    folder_path = st.text_input("Enter the folder path containing resumes")

    submit = st.button("Submit")

    if submit:
        if folder_path:
            file_list = [f for f in os.listdir(folder_path) if f.endswith('.pdf') or f.endswith('.docx')]
            total_files = len(file_list)
            data = []
            
            if total_files == 0:
                st.warning("No PDF or DOCX files found in the provided folder path.")
            else:
                progress_bar = st.progress(0)
                progress_text = st.empty()

                # Iterate through the files in the folder
                for idx, filename in enumerate(file_list):
                    file_path = os.path.join(folder_path, filename)
                    try:
                        if filename.endswith('.pdf'):
                            text = input_pdf_text(file_path)
                        elif filename.endswith('.docx'):
                            text = input_docx_text(file_path)

                        formatted_prompt = input_prompt.format(text=text)
                        response = get_gemini_response(formatted_prompt)

                        # Replace single quotes with double quotes (if necessary) and remove newlines
                        response = re.sub(r"'", '"', response)
                        response = response.replace('\n', ' ')

                        # Use regex to extract each field
                        name = re.search(r"Name:\s*(.*?),", response).group(1) if re.search(r"Name:\s*(.*?),", response) else 'Null'
                        phone = re.search(r"Phone Number:\s*(.*?),", response).group(1) if re.search(r"Phone Number:\s*(.*?),", response) else 'Null'
                        email = re.search(r"Email ID:\s*(.*?),", response).group(1) if re.search(r"Email ID:\s*(.*?),", response) else 'Null'
                        job_title = re.search(r"Job Title:\s*(.*?),", response).group(1) if re.search(r"Job Title:\s*(.*?),", response) else 'Null'
                        current_company = re.search(r"Current Company:\s*(.*?),", response).group(1) if re.search(r"Current Company:\s*(.*?),", response) else 'Null'
                        skills_match = re.search(r"Skills:\s*\[(.*?)\]", response)
                        skills = skills_match.group(1).replace('\\"', '') if skills_match else 'Null'
                        location = re.search(r"Location:\s*(.*?)(,|$)", response).group(1) if re.search(r"Location:\s*(.*?)(,|$)", response) else 'Null'

                        # Append the extracted data to the data list
                        data.append({
                            'Name': name.strip(),
                            'Phone Number': phone.strip(),
                            'Email ID': email.strip(),
                            'Job Title': job_title.strip(),
                            'Current Company': current_company.strip(),
                            'Skills': skills.strip(),
                            'Location': location.strip()
                        })

                    except Exception as e:
                        st.error(f"Error processing file {filename}: {e}")
                    
                    # Update progress bar
                    progress_percentage = (idx + 1) / total_files * 100
                    progress_bar.progress(int(progress_percentage))
                    progress_text.text(f"Processing file {idx + 1} of {total_files}")

            # Create a DataFrame and save to CSV
            if data:
                df = pd.DataFrame(data)

                # Display the DataFrame in Streamlit
                if df.shape[0] > 5:
                    df_1 = df.head(5)
                    
                    st.write(df_1[['Name','Phone Number','Email ID']])
                else:
                    st.write(df[['Name','Phone Number','Email ID']]) 
                # Save the DataFrame to a CSV file
                df.to_csv('resumes_folder_output.csv', index=False)

                st.success("Your folder data has been successfully saved to resumes_folder_output.csv")
            else:
                st.warning("No data was extracted from the resumes.")
        else:
            st.error("Please enter a valid folder path.")

# Run the app
if __name__ == "__main__":
    app()
