import os
import tempfile
import fitz  # PyMuPDF
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def extract_text_from_pdf(pdf_content):
    """Extract text from a PDF file content."""
    text = ''
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(pdf_content)
        temp_path = temp_file.name

        pdf_document = fitz.open(temp_path)
        for page_number in range(pdf_document.page_count):
            page = pdf_document.load_page(page_number)
            text += page.get_text()

    pdf_document.close()  # Close the PDF document explicitly
    os.remove(temp_path)  # Remove the temporary file after use
    return text.replace("\xa0", "")  # Clean up non-breaking spaces

def get_most_similar_job(data, cv_vect, df_vect):
    """Return indices of the most similar jobs based on cosine similarity."""
    # Calculate cosine similarities
    distances = cosine_similarity(cv_vect, df_vect).flatten()  # Flatten to 1D array
    indices = np.argsort(distances)[::-1]  # Sort by similarity in descending order
    return indices

import re

def extract_section_from_cv(cv_text, section_name):
    """
    Extracts a specific section from the CV text.
    Args:
        cv_text (str): The text extracted from the CV.
        section_name (str): The name of the section to extract (e.g., 'Skills', 'Experience').
    Returns:
        str: The extracted section or an empty string if not found.
    """
    section_pattern = rf"{section_name}.*?(?=\n[A-Z]|$)"
    match = re.search(section_pattern, cv_text, re.IGNORECASE | re.DOTALL)
    return match.group(0).strip() if match else ""


