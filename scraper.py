#scraping libraries
import requests
from bs4 import BeautifulSoup

#llm libraries
from openai import OpenAI
from groq import Groq

import base64

import os

from screenshot import take_screenshot

def scrape_url(url):
    response = requests.get(url)
    api = "groq"

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        #Extract page title:
        title = soup.title.get_text(strip=True)

        #Extract page text:
        body = soup.body

        elements = []
        if body:
            for tag in body.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li'], recursive=True):
                elements.append(tag.get_text(strip=True))
        
        #Combine title and text:
        page_text = f"{title}\n\n" + "\n\n".join(elements)

        # call return_info to sort through all the webpage text
        if api=="groq":
            info = return_info_with_groq(page_text)
        else:
            info = return_info_with_gpt(page_text)

        #check if no responsibilities were found. The length also checked in case the responsibilities happens to contain the words "none" or "not found"
        if (not info["Responsibilities"]) or (len(info["Responsibilities"]) < 12):
            #if ("None" in info["Responsibilities"] or "Not Found" in info["Responsibilities"]):
            print("none, encountered")
            take_screenshot(url, "page_screenshot.png")
            image = encode_image("page_screenshot.png")
            info = return_info_from_image(image)

        info["URL"] = url
        return info
    
    else:
        print("Error reaching the website, please submit the page text directly")
        return None

def scrape_text(page_text, url):
    api = "groq"

    if api=="groq":
        info = return_info_with_groq(page_text)
    else:
        info = return_info_with_gpt(page_text)
    
    info["URL"] = url
    return info

def return_info_with_gpt(page_text):
    #ask the GPT API to return the summary info
    client = OpenAI()
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You will be provided with the text from a job posting. Return the following details about the job: Title, Company, Location (or region, if exact location not found), Responsibilities, Company_Summary (not about their equal opportunities), Start_Date (such as year, season), Deadline (year/season/rolling if specific date not available), Posting_Date. If any of the information cannot be found in the text, respond with 'Not Found.'."},
            {"role": "system", "name":"example_user", "content": example_text1},
            {"role": "system", "name": "example_assistant", "content": example_response1},
            {"role": "system", "name":"example_user", "content": example_text2},
            {"role": "system", "name": "example_assistant", "content": example_response2},
            {"role": "user", "content": page_text}
        ]
    )
    #count the RESPONSE tokens, good to know:
    #token_count = completion.usage.prompt_tokens
    #print(token_count)

    #extract the actual completion text
    response = completion.choices[0].message.content

    #call create_dict to create a dictionary with all the info, based on the structure requested from the API.
    info = create_dict(response)
    return info

def return_info_with_groq(page_text):
    #ask the groq API to return the summary info
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    chat_completion = client.chat.completions.create(
    messages=[
            {"role": "system", "content": "You will be provided with the text from a job posting. Return the following details about the job: Title, Company, Location (or region, if exact location not found), Responsibilities, Company_Summary (not about their equal opportunities), Start_Date (such as year, season), Deadline (year/season/rolling if specific date not available), Posting_Date. If any of the information cannot be found in the text, respond with 'Not Found.'."},
            {"role": "system", "name":"example_user", "content": example_text1},
            {"role": "system", "name": "example_assistant", "content": example_response1},
            {"role": "system", "name":"example_user", "content": example_text2},
            {"role": "system", "name": "example_assistant", "content": example_response2},
            {"role": "user", "content": page_text}
    ],
    model="llama3-8b-8192",
    )

    #extract the actual completion text
    response = chat_completion.choices[0].message.content

    #call create_dict to create a dictionary with all the info, based on the structure requested from the API.
    info = create_dict(response)
    return info

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')
  
def return_info_from_image(image):
    #ask the GPT API to return the summary info
    client = OpenAI()

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
        {"role": "system", "content": "You will be provided with an image containing the text from a job posting. Return the following details about the job: Title, Company, Location (or region, if exact location not found), Responsibilities, Company_Summary (not about their equal opportunities), Start_Date (such as year, season), Deadline (year/season/rolling if specific date not available), Posting_Date. If any of the information cannot be found in the text, respond with 'Not Found.'."},
        {"role": "system", "name":"example_user", "content": example_text1},
        {"role": "system", "name": "example_assistant", "content": example_response1},
        {"role": "system", "name":"example_user", "content": example_text2},
        {"role": "system", "name": "example_assistant", "content": example_response2},
        {"role": "user",
        "content": [
            {
            "type": "text",
            "text": "provide me the requested info for this photo."
            },
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{image}"
            }
            }
        ]
        }
    ]
    )

    #extract the actual completion text
    response = completion.choices[0].message.content
    print("4o-mini vision was used")

    #call create_dict to create a dictionary with all the info, based on the structure requested from the API.
    info = create_dict(response)
    return info

def create_dict(response):
    lines = response.strip().split('\n')
    keys = ['Title', 'Company', 'Location', 'Responsibilities', 'Company_Summary', 'Start_Date', 'Deadline', 'Posting_Date', 'URL']
    job_details = dict.fromkeys(keys)

    for line in lines:
        # Split each line into key and value based on the first colon encountered
        parts = line.split(':', 1)
        if len(parts) == 2:
            key = parts[0].strip()
            key = key.replace('*', '')
            if key not in job_details:
                continue
            value = parts[1].strip()
            job_details[key] = value

    return job_details


example_text1 = """
2025 Full-Time Analyst Program - EMEA
Region  
EMEA
Recruitment Year  
2025
Program  
Analyst Program
Job description  
The Full-Time Analyst Programme is for candidates who will graduate with a bachelor’s or master’s degree between September 2024 and July 2025.

Our Full-Time Analyst Programme is a two-year experience designed to empower and support Analysts in connecting their personal passions and strengths to BlackRock’s mission, principles and purpose. The programme begins with an orientation to learn about our purpose, business and strategic priorities – all while gaining insights into the day-to-day life of an Analyst at BlackRock.

Following orientation, Analysts join their teams and stay connected with colleagues across the globe through ongoing training and professional development. This programme offers Analysts the chance to have a lasting impact on the firm and contribute to our greater collective purpose of helping more and more people experience financial well-being.

Important:
Candidates can apply for up to two functions within that programme (e.g., Investment Research and Analytics & Modeling). You must apply for both opportunities using the same programme application.

If you withdraw your application, you cannot submit another application for this programme this year.

Next steps:
Once you submit your application, you will receive an email to complete a pre-interview assessment. You have up to five days to submit your pre-interview assessment; if you fail to do so, your application will be automatically withdrawn.

We look forward to reviewing your application!

BlackRock is proud to be an Equal Opportunity Employer. We evaluate qualified applicants without regard to age, disability, race, religion, sex, sexual orientation and other protected characteristics at law.

Posted On:
10/07/2024

"""

example_response1 = """
Title: Full-Time Analyst Program.
Company: BlackRock.
Location: EMEA.
Responsibilities: The program is a two-year experience to empower and support Analysts in connecting their personal passions and strengths to BlackRock’s mission, principles, and purpose. The program includes an orientation, joining teams, ongoing training, and professional development to contribute to BlackRock's collective purpose. Candidates can apply for up to two functions within the program.
Company_Summary: BlackRock is a global investment management corporation.
Start_Date: Not Found.
Deadline: Not Found.
Posting_Date: 10 July 2024.
"""

example_text2 = """
Graduate Software Engineer
Computing, IT, Web Development, Systems, Software.
What you’ll be doing:
Create cutting edge software for our hardware and be involved in the entire lifecycle of a product, from design and development to integration. Work closely with both Electronic and Systems engineers, you'll enable the development of complex real-world systems that have to perform perfectly every time, as the consequences of failure could be catastrophic.

What’s in it for you?
Driven by a passion for developing world-class defence products; with ground-breaking technology, a collaborative culture and endless opportunities – you'll be part of a team building the future, today. Work-life balance is very important; you’ll get 25 days holiday, a flexible benefits package, a competitive pension scheme, cycle to work scheme and dedicated training to help you develop your career.

You’ll be part of an inclusive, supportive team throughout your programme, and empowered to take your career in the direction that suits you.

Location:
Barrow-in-Furness (Cumbria), New Malden (London), Frimley (Surrey), Broad Oak (Hampshire), Warton (Lancashire) and Brough (Hull)

Salary:
Our starting salary is £34,000, plus a £2,000 welcome payment along with an optional 20% salary advance. Plus a flexible package of benefits to suit your lifestyle.

Entry requirements?
You’ll need a minimum 2:2 Bachelor’s degree in a subject related to your chosen area.

Please note: some roles at BAE Systems are subject to security and export control restrictions and your nationality or place of birth may limit the roles you can undertake.

What is the application process?
The stages of our application process include: a short online application. If you’re successful, you'll then complete an online assessment with interactive activities, and an on-demand video interview. The next stage is competency-based interview, either virtual or face-to-face.

Why a BAE Systems programme?
We offer a non-rotational programme that gives you the choice of where you want to specialise - you’ll to deep-dive into your chosen field and develop your expertise, from day one.  You’ll also have the opportunity to pace your own development over 18-30 months, to suit your lifestyle.

Deadline:
Ongoing

Start Date: January/April 2025
"""

example_response2 = """
Title: Graduate Software Engineer.
Company: BAE Systems.
Location: Barrow-in-Furness (Cumbria), New Malden (London), Frimley (Surrey), Broad Oak (Hampshire), Warton (Lancashire) and Brough (Hull).
Responsibilities: As a Graduate Software Engineer, you will develop cutting-edge software for hardware, participating in the product lifecycle from design to integration, and collaborate with Electronic and Systems engineers to ensure flawless performance in complex systems.
Company_Summary: BAE Systems is a global defense and aerospace company, specializing in advanced technology solutions for military and commercial customers.
Start_Date: January/April 2025.
Deadline: Rolling.
Posting_Date: Not Found.
"""

#TEST CODE:
#url1 = "https://careers.blackrock.com/job/20418142/analyst-associate-investment-product-strategy-multi-asset-strategies-solutions-budapest-hu/"
#url2 = "https://blackrock.tal.net/vx/brand-3/spa-1/candidate/so/pm/1/pl/1/opp/8160-2025-Full-Time-Analyst-Program-EMEA/en-GB"
#url3 = "https://boards.greenhouse.io/gaintheory/jobs/7427938002"
#outputs = scrape_posting(url3)
#for key, value in outputs.items():
#    print(f"{key}: {value}")