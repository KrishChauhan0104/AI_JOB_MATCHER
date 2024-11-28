import threading
from functions import extract_text_from_pdf, get_most_similar_job, extract_section_from_cv
from fastapi import UploadFile, HTTPException, FastAPI
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util

# Initialize FastAPI app
app = FastAPI(project_name="cv")

# Global variables
summarizer = None
summ_data = []
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Initialize summarizer
def define_summarizer():
    global summarizer
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    print("\n\nSummarizer initialized!")

define_thread = threading.Thread(target=define_summarizer)
define_thread.start()

# Summarization utilities
def fit_threads(text):
    define_thread.join()  # Ensure summarizer is ready

    threads = []
    for t in text:
        thread = threading.Thread(target=summarization, args=(t,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()
    print("Summarization Done")

def summarization(text_part):
    global summ_data
    part = summarizer(text_part, max_length=150, min_length=30, do_sample=False)
    summ_data.append(part[0]["summary_text"].replace("\xa0", ""))

# Load dataset
df = pd.read_csv("all.csv")
concatenated_column = pd.concat([
    df['job_title'] + df['job_description'] + df['job_requirements'],
    df['city_name']
], axis=1).astype(str).agg(''.join, axis=1)
vectorizer = TfidfVectorizer(stop_words='english')
vectorizer.fit(concatenated_column)
df_vect = vectorizer.transform(concatenated_column)

@app.get("/")
async def read_root():
    return {"Hello": "World, Project name is : CV Description"}

@app.post("/prediction")
async def detect(cv: UploadFile, number_of_jobs: int):
    if not isinstance(number_of_jobs, int) or not (1 <= number_of_jobs <= df.shape[0]):
        raise HTTPException(
            status_code=415, detail=f"Please enter the number of jobs as an integer between 1 and {df.shape[0]}"
        )

    if cv.filename.split(".")[-1] != "pdf":
        raise HTTPException(status_code=415, detail="Please upload a PDF file.")

    cv_data = extract_text_from_pdf(await cv.read())
    index = len(cv_data) // 3
    text = [cv_data[:index], cv_data[index:2*index], cv_data[2*index:]]
    fit_threads(text)

    data = " .".join(summ_data)
    summ_data.clear()
    cv_vect = vectorizer.transform([data])
    indices = get_most_similar_job(data=data, cv_vect=cv_vect, df_vect=df_vect)

    prediction_data = df.iloc[indices[:number_of_jobs]].applymap(str).to_dict(orient='records')
    return {"prediction": prediction_data}

@app.post("/ats-score")
async def calculate_ats_score(cv: UploadFile):
    if cv.filename.split(".")[-1] != "pdf":
        raise HTTPException(status_code=415, detail="Please upload a PDF file.")

    cv_text = extract_text_from_pdf(await cv.read())

    # Calculate similarity scores with all jobs
    cv_embedding = model.encode(cv_text, convert_to_tensor=True)
    job_embeddings = model.encode(df['job_description'].tolist(), convert_to_tensor=True)
    similarity_scores = util.pytorch_cos_sim(cv_embedding, job_embeddings).cpu().numpy()[0]

    top_jobs = df.iloc[similarity_scores.argsort()[-5:][::-1]]  # Top 5 most similar jobs

    # Section-wise scoring (Optional)
    sections = {
        "Skills": ["Python", "Machine Learning", "JavaScript"],  # Example keywords
        "Experience": ["Developer", "Engineer", "Manager"],
    }
    section_scores = {}
    for section, keywords in sections.items():
        section_text = extract_section_from_cv(cv_text, section)
        score = sum(1 for kw in keywords if kw.lower() in section_text.lower()) / len(keywords) * 100
        section_scores[section] = round(score, 2)

    return {
        "similar_jobs": top_jobs.to_dict(orient="records"),
        "section_scores": section_scores,
        "feedback": {
            "missing_keywords": [kw for section in sections.values() for kw in section if kw.lower() not in cv_text.lower()],
            "sections_to_improve": [s for s, v in section_scores.items() if v < 70]
        }
    }


