from sentence_transformers import SentenceTransformer
import sqlite3
import json
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

def vectorize(id):
    conn = sqlite3.connect('jobs.db')
    conn.row_factory = sqlite3.Row  # This allows you to access columns by name
    cursor = conn.cursor()
    job = conn.execute('SELECT Title, Location, Responsibilities, Company_summary, Start_Date, Deadline, Posting_Date FROM job_applications WHERE id = ?', (id,)).fetchone()
    Title, Location, Responsibilities, Company_summary, Start_Date, Deadline, Posting_Date = job
    text = f"Title: {Title}. Location: {Location}. Responsibilities: {Responsibilities}. Company Summary: {Company_summary}. Start Date: {Start_Date}. Deadline: {Deadline}. Posting Date: {Posting_Date}."

    print(text)
    #create embedding model
    #model = SentenceTransformer('all-MiniLM-L6-v2')
    embedding = model.encode(text)
    
    # Convert embedding to JSON string
    embedding_json = json.dumps(embedding.tolist())
 
    cursor.execute("UPDATE job_applications SET Embedding = ? WHERE id = ?", (embedding_json, id))
    conn.commit()
    conn.close()


def search(query):
    conn = sqlite3.connect('jobs.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT id, Embedding FROM job_applications')
    rows = cursor.fetchall()

    query_embedding = model.encode(query)

    results = []
    for row in rows:
        job_id, embedding_json = row
        job_embedding = np.array(json.loads(embedding_json))
        similarity = np.dot(query_embedding, job_embedding) / (np.linalg.norm(query_embedding) * np.linalg.norm(job_embedding))
        results.append((job_id, similarity))
    
    # Sort results by similarity score in descending order
    results.sort(key=lambda x: x[1], reverse=True)
    print()
    
    # Retrieve the top N matching jobs
    top_n = 3  # Change this number to the desired number of results
    top_job_ids = [result[0] for result in results[:top_n]]

    if top_job_ids:
        placeholders = ','.join(['?'] * len(top_job_ids))
        cursor.execute(f'SELECT * FROM job_applications WHERE id IN ({placeholders})', top_job_ids)
        matching_jobs = cursor.fetchall()
        
        # Convert to list of dictionaries
        matching_jobs_dicts = [dict(job) for job in matching_jobs]
        
        # Sort jobs by the order of top_job_ids
        id_to_job = {job['id']: job for job in matching_jobs_dicts}
        sorted_matching_jobs = [id_to_job[job_id] for job_id in top_job_ids]
    else:
        sorted_matching_jobs = []

    conn.close()
    return sorted_matching_jobs