from flask import Flask, request, render_template
import pandas as pd
import sqlite3
from scraper import scrape_url, scrape_text
from database import export_excel, url_exists_in_db


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit_url', methods=['POST'])
def add_job():
    url = request.form['url']
    page_text = request.form['page_text']

    if url_exists_in_db(url):
        return render_template('already_saved.html')

    if len(page_text)==0: #if no additional text is submitted, scrape from the URL.
        scraped_details = scrape_url(url)
    else: #if text has been submitted, scrape only from the text.
        scraped_details = scrape_text(page_text, url)
    
    if scraped_details is not None:
        conn = sqlite3.connect('jobs.db')
        job_data = pd.DataFrame([scraped_details])
        job_data.to_sql('job_applications', conn, if_exists='append', index=False)
        
        return render_template('success.html', job_details=scraped_details)
    else:
        return render_template('failure.html')

@app.route('/view_jobs')
def view_jobs():
    conn = sqlite3.connect('jobs.db')
    df = pd.read_sql('SELECT * FROM job_applications', conn)
    return render_template('view_jobs.html', jobs=df.to_dict(orient='records'))

@app.route('/export_jobs')
def export_jobs():
    export_excel()
    return render_template('jobs_exported.html')

if __name__ == '__main__':
    app.run(debug=True)