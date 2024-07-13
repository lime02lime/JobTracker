#scraping libraries
import requests
from bs4 import BeautifulSoup

#GPT libraries
from openai import OpenAI
client = OpenAI()

def scrape_posting(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    #Extract page title:
    title = soup.title.get_text(strip=True)

    # Extract text from all <p> tags
    paragraphs = [p.get_text(strip=True) for p in soup.find_all('p')]

    # Combine the extracted information
    page_text = f"{title}\n\n" + "\n\n".join(paragraphs)

    # call return_info to sort through all the webpage text
    info = return_info(page_text)

    for key, value in info.items():
        print(f"{key}: {value}")
    return info

def return_info(page_text):
    #ask the GPT API to return the summary info
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You will be provided with the text from a job posting. Return the following details about the job: title, company, location (or region, if exact location not found), a summary of key responsibilities and job activities, a short summary of what the company does (not about their equal opportunities), start date or approximate period (such as year, season), application deadline (year/season/rolling if specific date not available), job posting date. If any of the information cannot be found in the text, respond with Not Found."},
            {"role": "user", "content": f"Return the information requested with one item per line, in this format: 'Title:\\n(text). Company:\\n(text). Location:\\n(text). Responsibilities:\\n(text). Company Summary:\\n(text). Start Date:\\n(text). Deadline:\\n(text). Posting Date:\\n(text).' Here is the text: {page_text}"}
        ]
    )
    #count the RESPONSE tokens, good to know:
    token_count = completion.usage.prompt_tokens
    print(token_count)

    #extract the actual completion text
    response = completion.choices[0].message.content

    #call create_dict to create a dictionary with all the info, based on the structure requested from the API.
    info = create_dict(response)
    return info
    

def create_dict(response):
    #split the text by newlines
    lines = response.strip().split('\n')
    #create the final dictionary
    job_details = {}

    # Helper variables
    current_key = None
    current_value = []

    # Iterate over the lines
    for line in lines:
        # Check if the line ends with a colon, as all the titles do
        if line.endswith(':'):
            # If there's a current key being processed, save it to the dictionary
            if current_key:
                job_details[current_key] = ' '.join(current_value).strip()
            # Set the new key and reset the value list
            current_key = line[:-1].strip()  # Remove the colon
            current_value = []
        else:
            # Accumulate the lines for the current key
            current_value.append(line.strip())

    # Add the last section to the dictionary
    if current_key:
        job_details[current_key] = ' '.join(current_value).strip()

    return job_details


#TEST CODE:
#outputs = scrape_posting("https://blackrock.tal.net/vx/brand-3/spa-1/candidate/so/pm/1/pl/1/opp/8160-2025-Full-Time-Analyst-Program-EMEA/en-GB")
#for key, value in outputs.items():
#    print(f"{key}: {value}")