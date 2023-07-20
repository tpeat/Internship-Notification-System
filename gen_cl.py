import requests
from bs4 import BeautifulSoup
import pdfkit
import openai
from dotenv import load_dotenv
import json
import os
import datetime
import time

load_dotenv()
NAME = os.environ.get("NAME")
ADDRESS = os.environ.get("ADDRESS")
PHONE = os.environ.get("PHONE")
EMAIL = os.environ.get("EMAIL")
SALARY = os.environ.get("SALARY")
START_DATE = os.environ.get("START_DATE")
openai.api_key = os.environ.get("OPENAI_API_KEY")
MAX_RETRIES = 3
RETRY_DELAY = 30

# Read your resume file
with open("resume.txt", "r") as f:
    resume_content = f.read()

# completion model
def get_completion(prompt, model="gpt-3.5-turbo", temperature=0): 
    retries = 0
    while retries < MAX_RETRIES:
        try:
            messages = [{"role": "user", "content": prompt}]
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=temperature,  # degree of randomness of GPT response
            )
            return response.choices[0].message["content"]
        except openai.OpenAIError as e:
            print("An error occurred while making the API call:", e)
            retries += 1
            if retries < MAX_RETRIES:
                print(f"Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                print("Max retries reached. Aborting.")
                return None
# Delimiter used to mark the start and end res and job desc
delimiter = "####"

# Prompt for extracting information from resume
extraction_prompt = f"""
Your task is to extract information about the education, work experience, skills,
motivation from the resume marked with {delimiter} characters.

Format your answer as a Python dictionary with "education", "work experience", "skills", 
and "motivation" as keys.

If the information is missing in the resume, use "unknown" as the value.

Respond as concisely as possible.

Resume: {delimiter}{resume_content}{delimiter}
"""

res_extraction_response_str = get_completion(extraction_prompt)
# Convert extraction response from str to json
res_extraction_response = json.loads(res_extraction_response_str)
# Show extracted information
print(res_extraction_response)

########### Job Description ############
# get job description
url = "https://careers.point72.com/CSJobDetail?jobName=summer-2024-quantitative-developer-internship&jobCode=CSS-0010069"
url = "https://app.ripplematch.com/v2/public/job/6f5894f6/details?utm_source=RM&utm_medium=organic_social&utm_campaign=growth_github&utm_content=kpmg&utm_term=null"
url = "https://optiver.com/working-at-optiver/career-opportunities/6793142002/"
url_response = requests.get(url)

# Extract the HTML content from the response
html_content = url_response.text

# Create a BeautifulSoup object to parse the HTML
soup = BeautifulSoup(html_content, "html.parser")

# Extract the text from the webpage
job_description = soup.get_text()

# Remove whitespace characters
job_description = " ".join(job_description.split())  

print(job_description)

# Prompt for extracting information from job description
extraction_prompt = f"""
Your task is to extract information about the employer, job title, requirements, tasks, 
contact person, and address from the job description marked with {delimiter} characters.

Format your answer as a Python dictionary with "employer", "job title", "requirements", 
"tasks", "contact person", and "address" as keys.

Format the "requirements" and "tasks" as lists.

If the information is missing in the job description, use "unknown" as the value.

Respond as concisely as possible.

Job description: {delimiter}{job_description}{delimiter}
"""

# Get extraction response
extraction_response_str = get_completion(extraction_prompt)

# Convert extraction response from str to json
extraction_response = json.loads(extraction_response_str)

# Show extracted information
print(extraction_response)


# create cover letter
# Cover letter prompt
cover_letter_prompt = f"""
Your task is to create a professional cover letter.

Address the letter to the following employer, address, job position, and contact person:
Employer: {extraction_response["employer"]}
Address: {extraction_response["address"]}
Job Position: {extraction_response["job title"]}
Contact Person: {extraction_response["contact person"]}

Use the following sender information:
Name: {NAME}
Address: {ADDRESS}
Phone Number: {PHONE}
Email: {EMAIL}

Include the location and date in the letterhead of the cover letter.
Use the location from: {ADDRESS}
Use the current date in the English date format: {datetime.date.today()}

Describe how the education, work experience, skills, and motivation fulfill 
the job requirements and tasks. Use the following information:
Requirements: {extraction_response["requirements"]}
Tasks: {extraction_response["tasks"]}
Education: {res_extraction_response['education']}
Work Experience: {res_extraction_response['work experience']}
Skills: {res_extraction_response['skills']}
Motivation: {res_extraction_response['motivation']}

State the salary expectations and possible start date as follows:
Salary Expectations: {SALARY}
Possible Start Date: {START_DATE}

Write in a professional, concise, and compact tone.

Sign the cover letter as {NAME}.
"""

cover_letter_response = get_completion(cover_letter_prompt, temperature=0.7)

# Save the generated cover letter as a PDF
pdfkit.from_string(cover_letter_response, "cover_letter.pdf")