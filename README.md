# app-manager
This program is to help keep track of job applications.

The idea is that a job advert URL is input, which the program opens and web scrapes. The information is fed to a the Groq (free, and works just as well) or GPT API which finds the desired information and stores it in a database.

If the model fails to find the information in the website html, we use Selenium to take a screenshot of the web page, and then use gpt-4o vision capabilities to find the info from that screenshot.
