import streamlit as st
import requests
import pandas as pd

# Apply Custom Styling for Modern Design
st.set_page_config(
    page_title="AI Job Matcher",
    page_icon="🔍",
    layout="centered",
)

# Custom CSS Styling
st.markdown(
    """
    <style>
        /* General Layout */
        body {
            background-color: #f9f9f9;
            font-family: 'Arial', sans-serif;
        }
        .main {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        }
        h1, h2, h3 {
            color: #333333;
        }
        .stButton>button {
            color: white;
            background-color: #4CAF50;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
        }
        .stButton>button:hover {
            background-color: #45a049;
        }
        .stDataFrame {
            margin-top: 20px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Title and Description
st.title("🔍 AI Job Matcher")
st.markdown(
    """
    Welcome to the **AI Job Matcher App**! This smart tool analyzes your resume 
    and provides tailored job recommendations. Enhance your job search process in just a few clicks!
    """
)

# Tabs for Navigation
tabs = st.tabs(["📂 Job Recommendations", "✅ ATS Checker"])

# --- Job Recommendations Tab ---
with tabs[0]:
    st.subheader("📂 Upload Your Resume")
    st.markdown(
        """
        Upload your resume as a PDF to receive tailored job recommendations.  
        Use the input box below to specify the number of jobs you'd like to retrieve.
        """
    )
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"], key="job_recommendation")
    
    if uploaded_file:
        st.success("Resume uploaded successfully! 🎉")

    # Input for Number of Job Recommendations
    st.subheader("📊 Number of Job Recommendations")
    number_of_jobs = st.number_input(
        "Specify the number of jobs:",
        min_value=1,
        max_value=50,
        value=10,
        step=1,
        help="Choose the number of jobs you'd like to see."
    )

    # Prediction Button
    if st.button("🔎 Get Job Recommendations"):
        if uploaded_file:
            # Mock API interaction (Replace with actual API calls)
            files = {"cv": ("file.pdf", uploaded_file)}
            params = {"number_of_jobs": number_of_jobs}
            api_url = "http://127.0.0.1:8000/prediction"
            
            response = requests.post(api_url, files=files, params=params)
            
            if response.status_code == 200:
                prediction_data = response.json().get("prediction", [])
                if prediction_data:
                    st.subheader("✨ Recommended Jobs")
                    data_df = pd.DataFrame(prediction_data)
                    st.dataframe(data_df)
                else:
                    st.warning("No recommendations found. Try again with different settings.")
            else:
                st.error(f"Error fetching recommendations: {response.status_code}")
        else:
            st.warning("Please upload your resume first!")

# --- ATS Checker Tab ---
with tabs[1]:
    st.subheader("✅ ATS Compatibility Checker")
    st.markdown(
        """
        Ensure your resume is ATS-compatible! Upload your resume as a PDF to check its ATS compatibility score and get actionable feedback.
        """
    )
    ats_cv = st.file_uploader("Upload Resume for ATS Analysis", type=["pdf"], key="ats_checker")
    
    if st.button("✅ Check ATS Compatibility"):
        if ats_cv:
            # Mock API interaction (Replace with actual API calls)
            files = {"cv": ("file.pdf", ats_cv)}
            response = requests.post("http://127.0.0.1:8000/ats-checker", files=files)
            
            if response.status_code == 200:
                ats_response = response.json()
                ats_score = ats_response.get("ats_score", "N/A")
                feedback = ats_response.get("feedback", {})
                
                st.success(f"ATS Compatibility Score: **{ats_score}%**")
                st.markdown("### 📌 Feedback:")
                missing_keywords = feedback.get("missing_keywords", [])
                improvement_tips = feedback.get("improvement_tips", [])
                
                if missing_keywords:
                    st.markdown("**Missing Keywords:**")
                    st.write(", ".join(missing_keywords))
                
                if improvement_tips:
                    st.markdown("**Improvement Tips:**")
                    for tip in improvement_tips:
                        st.write(f"• {tip}")
            else:
                st.error(f"Error: {response.status_code}")
        else:
            st.warning("Please upload your resume to check its ATS compatibility!")

# Footer
st.markdown("---")
st.markdown(
    """
    ### About AI Job Matcher
    This app uses AI-powered tools to simplify your job search process. Tailor-made for individuals looking to optimize their career opportunities.
    """
)
