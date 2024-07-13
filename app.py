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
    job_details = scrape_posting(url)
    
    conn = sqlite3.connect('jobs.db')
    job_data = pd.DataFrame([job_details])
    print(job_data.to_sql('job_applications', conn, if_exists='append', index=False))
    job_data.to_sql('job_applications', conn, if_exists='append', index=False)
    
    return render_template('success.html', job_details=job_details)

@app.route('/view_jobs')
def view_jobs():
    conn = sqlite3.connect('jobs.db')
    df = pd.read_sql('SELECT * FROM job_applications', conn)
    return render_template('view_jobs.html', jobs=df.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)