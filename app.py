from flask import Flask, request, render_template
import pandas as pd
import sqlite3
from scraper import scrape_posting

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_job', methods=['POST'])
def add_job():
    url = request.form['url']

    if url_exists_in_db(url):
        return render_template('already_saved.html')

    job_details = scrape_posting(url)
    
    if job_details is not None:
        conn = sqlite3.connect('jobs.db')
        job_data = pd.DataFrame([job_details])
        job_data.to_sql('job_applications', conn, if_exists='append', index=False)
        
        return render_template('success.html', job_details=job_details)
    
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