from flask import Flask, request, render_template, redirect, url_for
import pandas as pd
import sqlite3
from scraper import scrape_url, scrape_text
from database import export_excel, url_exists_in_db, initialize_database
from semantics import vectorize, search


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit_url', methods=['POST'])
def add_job():
    url = request.form['url']

    if url_exists_in_db(url):
        return render_template('already_saved.html')

    page_text = request.form['page_text']
    if len(page_text)==0: #if no additional text is submitted, scrape from the URL.
        scraped_details = scrape_url(url)
    else: #if text has been submitted, scrape only from the text.
        scraped_details = scrape_text(page_text, url)
    
    if scraped_details is not None:
        conn = sqlite3.connect('jobs.db')
        job_data = pd.DataFrame([scraped_details])
        job_data.to_sql('job_applications', conn, if_exists='append', index=False)
        
        id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
        vectorize(id)

        conn.commit()
        conn.close()
        
        return render_template('success.html', job_details=scraped_details, page_text=page_text, id=id)
    else:
        return render_template('failure.html')
    
@app.route('/regenerate', methods=["GET", "POST"])
def regenerate():
    url = request.form['url']
    id = request.form['id']
    page_text = request.form['page_text']

    if len(page_text)==0: #if no additional text is submitted, scrape from the URL.
        scraped_details = scrape_url(url)
    else: #if text has been submitted, scrape only from the text.
        scraped_details = scrape_text(page_text, url)
    
    if scraped_details is not None:
        conn = sqlite3.connect('jobs.db')
        conn.execute('DELETE FROM job_applications WHERE id = ?', (id,))
        conn.commit()
        job_data = pd.DataFrame([scraped_details])
        job_data.to_sql('job_applications', conn, if_exists='append', index=False)
        id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]

        vectorize(id)
        conn.commit()
        conn.close()
        return render_template('success.html', job_details=scraped_details, page_text=page_text, id=id)
    else:
        return render_template('failure.html')

@app.route('/view_jobs')
def view_jobs():
    conn = sqlite3.connect('jobs.db')
    df = pd.read_sql('SELECT * FROM job_applications', conn)
    jobs=df.to_dict(orient='records')
    conn.commit()
    conn.close()
    return render_template('view_jobs.html', jobs=jobs)



@app.route('/search_jobs', methods=['POST'])
def search_jobs():
    query = request.form['query']
    matching_jobs = search(query)

    return render_template('view_jobs.html', jobs=matching_jobs)




@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = sqlite3.connect('jobs.db')
    conn.row_factory = sqlite3.Row  # This allows you to access columns by name
    job = conn.execute('SELECT * FROM job_applications WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        title = request.form['title']
        company = request.form['company']
        location = request.form['location']
        responsibilities = request.form['responsibilities']
        company_summary = request.form['company_summary']
        start_date = request.form['start_date']
        deadline = request.form['deadline']
        posting_date = request.form['posting_date']
        url = request.form['url']

        conn.execute('''
            UPDATE job_applications
            SET Title = ?, Company = ?, Location = ?, Responsibilities = ?, 
                Company_Summary = ?, Start_Date = ?, Deadline = ?, Posting_Date = ?, URL = ?
            WHERE id = ?
        ''', (title, company, location, responsibilities, company_summary, start_date, deadline, posting_date, url, id))
        conn.commit()
        conn.close()

        return redirect(url_for('view_jobs'))

    job_dict = dict(job) #convert to dict so that when we load the edit page, we can pre-fill the text boxes with the existing entries.
    conn.close()
    return render_template('edit_job.html', job=job_dict)


@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    conn = sqlite3.connect('jobs.db')
    conn.row_factory = sqlite3.Row

    # Fetch the job to be deleted
    job = conn.execute('SELECT * FROM job_applications WHERE id = ?', (id,)).fetchone()
    job_dict = dict(job) if job else None
    
    if job:
        # Delete the job from the database
        conn.execute('DELETE FROM job_applications WHERE id = ?', (id,))
        conn.commit()
    else:
        view_jobs()

    conn.close()
    
    # Redirect to the confirmation page with the job ID
    return render_template('deletion.html', job=job_dict)

@app.route('/export_jobs')
def export_jobs():
    export_excel()
    return render_template('jobs_exported.html')

if __name__ == '__main__':
    initialize_database()
    app.run(debug=True)