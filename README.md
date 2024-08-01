# JobTracker
JobTracker is a web application built using Flask to help users keep track of their job applications. The app uses the Groq API (or GPT, depending on preference) to extract the key information from a submitted job posting url. Users can then view the key information about the job postings in a table format, edit the details manually, or delete entries.

Groq is an AI infrastructure company that claims to have the fastest AI inferencing. Their API is currently free to use and supposedly faster than the GPT API.

# Features
**Add job postings**: the url to a job posting can be submitted on the home screen, and the app web scrapes the information from that page. The chosen LLM API collects the key information and saves it into a locally stored database. If the API fails to return any useful information (e.g. due to the webside blocking web scraping), the app attempts to take a screenshot of the page instead. The screenshot is then submitted to gpt-4o which extracts the key information from the screenshot. If this is also not successful, the user can submit the actual webpage text directly into a text box (by copy/paste).

**Edit job postings**: Modify existing entries.

**Delete job postings**: Delete existing entries.

**View job postings**: View a table format of the saved job postings.

**Search jobs**: Perform semantic search of the database using vector embeddings, to find closely matching entries by company, location, job responsibilities, etc.

**Export jobs**: The database can be exported to .xlsx in case the user prefers to view it in Excel.

# Dependencies
These are listed in the requirements.txt file.

# Database
The database is created automatically when you run the app.

# File Descriptions
**app.py**: The main Flask application file which includes route handlers.

**scraper.py**: Contains functions for web scraping and for the LLM API's to extract the key info.

**database.py**: Contains functions relating to the database, including initialization, exporting to Excel, and checking for existing URLs (so that users don't add duplicate entries).

**semantics.py**: Contains functions to vectorize each database entry and handles semantic search functionality.

**screenshot.py**: Contains functions to screenshot the requested webpage in case the original web scraping does not return any useful results.
