import streamlit as st
st.set_page_config(page_title="Resume Analyzer", layout="wide")

import google.generativeai as genai
import PyPDF2
import docx
import plotly.graph_objects as go
import json
import re
import time

# Custom CSS for better styling with light/dark shade combination
st.markdown("""
<style>
    body {
        background-color: #F8FAFC;
        color: #1E293B;
    }
    .main-header {
        font-size: 2.5rem;
        color: #1E293B;
        text-align: center;
        padding: 1.5rem 0;
        font-weight: 700;
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .section-header {
        font-size: 1.5rem;
        color: #1E293B;
        padding: 0.5rem 0;
        font-weight: 600;
        border-bottom: 2px solid #3B82F6;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #EFF6FF;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #3B82F6;
        margin-bottom: 1rem;
    }
    .item-card {
        background-color: white;
        padding: 0.8rem;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        margin-bottom: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .skill-tag {
        display: inline-block;
        background-color: #DBEAFE;
        color: #1E40AF;
        padding: 0.3rem 0.6rem;
        border-radius: 15px;
        margin: 0.2rem;
        font-size: 0.9rem;
    }
    .strength-item {
        background-color: #ECFDF5;
        border-left: 3px solid #059669;
        padding: 0.8rem;
        margin-bottom: 0.5rem;
        border-radius: 5px;
    }
    .improvement-item {
        background-color: #FEF2F2;
        border-left: 3px solid #DC2626;
        padding: 0.8rem;
        margin-bottom: 0.5rem;
        border-radius: 5px;
    }
    .education-item {
        background-color: #F8FAFC;
        border-left: 3px solid #4B5563;
        padding: 0.8rem;
        margin-bottom: 0.5rem;
        border-radius: 5px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    .upload-section {
        background: linear-gradient(to bottom, #F1F5F9, #E2E8F0);
        padding: 2rem;
        border-radius: 10px;
        border: 2px dashed #94A3B8;
        text-align: center;
        margin-bottom: 2rem;
        transition: all 0.3s ease;
    }
    .upload-section:hover {
        border-color: #3B82F6;
        box-shadow: 0 4px 6px rgba(59, 130, 246, 0.1);
    }
    .upload-icon {
        font-size: 3rem;
        color: #64748B;
        margin-bottom: 1rem;
    }
    .upload-text {
        font-size: 1.2rem;
        color: #334155;
        margin-bottom: 1rem;
    }
    .file-types {
        font-size: 0.9rem;
        color: #64748B;
        margin-top: 0.5rem;
    }
    .stButton>button {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        color: white;
        border-radius: 5px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        border: none;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        transform: translateY(-2px);
    }
    .tab-container {
        background-color: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    /* Loading animation */
    @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
    .loading-pulse {
        animation: pulse 1.5s infinite ease-in-out;
        background-color: #E2E8F0;
        border-radius: 5px;
        height: 100px;
        margin-bottom: 1rem;
    }
    .divider {
        height: 1px;
        background: linear-gradient(to right, transparent, #CBD5E1, transparent);
        margin: 1.5rem 0;
    }
    /* Custom file upload button */
    .file-upload-btn {
        background-color: #3B82F6;
        color: white;
        padding: 0.7rem 1.5rem;
        border-radius: 5px;
        cursor: pointer;
        display: inline-block;
        margin-top: 1rem;
        font-weight: 500;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #F1F5F9;
        border-radius: 5px 5px 0 0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #DBEAFE;
    }
</style>
""", unsafe_allow_html=True)

# Configure Gemini API
genai.configure(api_key='AIzaSyAW3Wiqvh7iv9-uukyKFEQnZTK-UGO7xH0')

try:
    # Using Gemini 1.5 Pro model
    model = genai.GenerativeModel('models/gemini-1.5-pro')
except Exception as e:
    st.error(f"Failed to initialize Gemini API: {str(e)}")
    model = None

def read_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def read_docx(file):
    doc = docx.Document(file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def extract_json(text):
    """Extract JSON from text that may contain additional content."""
    # Look for JSON content between curly braces
    match = re.search(r'({[\s\S]*})', text)
    if match:
        potential_json = match.group(1)
        # Remove any comments
        clean_json = re.sub(r'//.*', '', potential_json)
        return clean_json
    return text

def analyze_resume(text):
    if model is None:
        return "Error: Gemini API not initialized properly"
    
    prompt = f"""Analyze this resume and provide the following in ONLY JSON format with no additional text or explanations:
    {{
        "skills": ["skill1", "skill2", ...],
        "years_of_experience": "X years",
        "education": ["degree1", "degree2", ...],
        "skill_scores": {{"skill1": score1, "skill2": score2, ...}},
        "key_strengths": ["strength1", "strength2", ...],
        "areas_of_improvement": ["area1", "area2", ...]
    }}
    
    Resume text:
    {text}
    """
    try:
        response = model.generate_content(prompt)
        
        # For debugging - can be hidden in production
        with st.expander("View Raw API Response", expanded=False):
            st.text(response.text)
        
        # Extract JSON from response
        json_content = extract_json(response.text)
        return json_content
    except Exception as e:
        st.error(f"Error during resume analysis: {str(e)}")
        return None

# Main UI
st.markdown('<div class="main-header">Resume Analyzer</div>', unsafe_allow_html=True)

# Two-column layout for the main content
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown('<div class="section-header">Resume Input</div>', unsafe_allow_html=True)
    
    # Improved upload section with clearer instructions
    st.markdown("""
    <div class="upload-section">
        <div class="upload-icon">📄</div>
        <div class="upload-text">Upload your resume</div>
        <div class="file-types">Supported formats: PDF, DOCX, and TXT</div>
    </div>
    """, unsafe_allow_html=True)
    
    # File uploader
    uploaded_file = st.file_uploader("", type=["pdf", "docx", "txt"], label_visibility="collapsed")
    
    # Add a divider
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Actions section
    st.markdown('<div class="section-header">Actions</div>', unsafe_allow_html=True)
    analyze_button = st.button("Analyze Resume")

# Main content area
with col2:
    if uploaded_file:
        # Show loading animation while reading file
        with st.spinner("Reading file..."):
            # Simulate loading for better UX
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
            
            # Read file content
            try:
                if uploaded_file.type == "application/pdf":
                    text = read_pdf(uploaded_file)
                elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    text = read_docx(uploaded_file)
                else:  # txt file
                    text = uploaded_file.getvalue().decode()
                
                # Remove progress bar after loading
                progress_bar.empty()
                
                st.markdown('<div class="section-header">Parsed Resume Content</div>', unsafe_allow_html=True)
                with st.expander("View Content", expanded=False):
                    st.text(text)
                
                if analyze_button:
                    # Loading animation for analysis
                    with st.spinner("Analyzing resume..."):
                        # Simulate loading for better UX
                        analysis_progress = st.progress(0)
                        for i in range(100):
                            time.sleep(0.02)
                            analysis_progress.progress(i + 1)
                        
                        analysis = analyze_resume(text)
                        analysis_progress.empty()
                        
                        if analysis:
                            try:
                                analysis_json = json.loads(analysis)
                                
                                # Create tabs for different sections
                                st.markdown('<div class="tab-container">', unsafe_allow_html=True)
                                tabs = st.tabs(["Overview", "Skills", "Education", "Strengths & Improvements"])
                                
                                # Overview Tab
                                with tabs[0]:
                                    # Two columns for basic info
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        st.markdown('<div class="section-header">Experience</div>', unsafe_allow_html=True)
                                        if "years_of_experience" in analysis_json:
                                            st.markdown(f'<div class="item-card">{analysis_json["years_of_experience"]}</div>', unsafe_allow_html=True)
                                    
                                    with col2:
                                        st.markdown('<div class="section-header">Total Skills</div>', unsafe_allow_html=True)
                                        if "skills" in analysis_json:
                                            st.markdown(f'<div class="item-card">{len(analysis_json["skills"])} skills identified</div>', unsafe_allow_html=True)
                                    
                                    # Skill Match Score chart
                                    if "skill_scores" in analysis_json and any(analysis_json["skill_scores"].values()):
                                        st.markdown('<div class="section-header">Skill Match Scores</div>', unsafe_allow_html=True)
                                        
                                        # Filter out null values
                                        filtered_skills = {k: v for k, v in analysis_json["skill_scores"].items() if v is not None}
                                        
                                        if filtered_skills:
                                            skills = list(filtered_skills.keys())
                                            scores = list(filtered_skills.values())
                                            
                                            fig = go.Figure(data=[
                                                go.Bar(x=skills, y=scores, 
                                                       marker_color='#3B82F6')
                                            ])
                                            fig.update_layout(
                                                title="Skill Match Scores",
                                                xaxis_title="Skills",
                                                yaxis_title="Match Score",
                                                plot_bgcolor='rgba(0,0,0,0)',
                                                height=400
                                            )
                                            st.plotly_chart(fig, use_container_width=True)
                                
                                # Skills Tab
                                with tabs[1]:
                                    st.markdown('<div class="section-header">Skills</div>', unsafe_allow_html=True)
                                    if "skills" in analysis_json:
                                        skills_html = '<div style="padding: 10px;">'
                                        for skill in analysis_json["skills"]:
                                            skills_html += f'<span class="skill-tag">{skill}</span>'
                                        skills_html += '</div>'
                                        st.markdown(skills_html, unsafe_allow_html=True)
                                
                                # Education Tab
                                with tabs[2]:
                                    st.markdown('<div class="section-header">Education</div>', unsafe_allow_html=True)
                                    if "education" in analysis_json:
                                        for edu in analysis_json["education"]:
                                            st.markdown(f'<div class="education-item">{edu}</div>', unsafe_allow_html=True)
                                
                                # Strengths & Improvements Tab
                                with tabs[3]:
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        st.markdown('<div class="section-header">Key Strengths</div>', unsafe_allow_html=True)
                                        if "key_strengths" in analysis_json:
                                            for strength in analysis_json["key_strengths"]:
                                                st.markdown(f'<div class="strength-item">{strength}</div>', unsafe_allow_html=True)
                                    
                                    with col2:
                                        st.markdown('<div class="section-header">Areas of Improvement</div>', unsafe_allow_html=True)
                                        if "areas_of_improvement" in analysis_json and analysis_json["areas_of_improvement"]:
                                            for area in analysis_json["areas_of_improvement"]:
                                                st.markdown(f'<div class="improvement-item">{area}</div>', unsafe_allow_html=True)
                                        else:
                                            st.markdown('<div class="info-box">No specific areas of improvement identified.</div>', unsafe_allow_html=True)
                                
                                st.markdown('</div>', unsafe_allow_html=True)
                                
                            except json.JSONDecodeError as e:
                                st.error(f"Failed to parse analysis results: {str(e)}")
                                st.error("Please try again.")
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
    else:
        # Show placeholder when no file is uploaded
        st.markdown("""
        <div style="background-color: #F8FAFC; padding: 3rem; border-radius: 10px; text-align: center; color: #64748B; border: 1px dashed #CBD5E1;">
            <h3>Upload a resume to see analysis results</h3>
            <p>The analyzer will extract skills, education, experience and provide insights.</p>
        </div>
        """, unsafe_allow_html=True)
