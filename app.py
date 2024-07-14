from flask import Flask, request, render_template
import pandas as pd
import sqlite3
from scraper import scrape_url, scrape_text

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

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

def table_exists(cursor, table_name):
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    result = cursor.fetchone()
    return result is not None

def url_exists_in_db(url):
    conn = sqlite3.connect('jobs.db')
    cursor = conn.cursor()

    if not table_exists(cursor, "job_applications"):
        return 0

    cursor.execute("SELECT COUNT(*) FROM job_applications WHERE URL=?", (url,))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

@app.route('/view_jobs')
def view_jobs():
    conn = sqlite3.connect('jobs.db')
    df = pd.read_sql('SELECT * FROM job_applications', conn)
    return render_template('view_jobs.html', jobs=df.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)