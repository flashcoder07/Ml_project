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
        background-color: #FFFFFF;
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
        margin-bottom: 2.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .section-header {
        font-size: 1.5rem;
        color: #1E293B;
        padding: 0.5rem 0;
        font-weight: 600;
        border-bottom: 2px solid #3B82F6;
        margin-top: 2rem;
        margin-bottom: 1.5rem;
    }
    .info-box {
        background-color: #EFF6FF;
        padding: 1.2rem;
        border-radius: 10px;
        border-left: 5px solid #3B82F6;
        margin-bottom: 1.5rem;
        margin-top: 0.8rem;
    }
    .item-card {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        margin-bottom: 1rem;
        margin-top: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
        border-left: 3px solidrgb(0, 0, 0);
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
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        margin-top: 1.5rem;
        margin-bottom: 2rem;
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
        height: 2px;
        background: linear-gradient(to right, transparent, #CBD5E1, transparent);
        margin: 2rem 0;
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
    /* Chart container styling */
    .chart-container {
        background-color: white;
        border-radius: 10px;
        padding: 1.2rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin: 1.5rem 0;
    }
    
    /* Section spacing */
    .section-spacing {
        margin-top: 2rem;
        margin-bottom: 2rem;
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
                                    
                                    st.markdown('<div class="section-spacing"></div>', unsafe_allow_html=True)
                                    
                                    # Skill Match Score chart
                                    if "skill_scores" in analysis_json and any(analysis_json["skill_scores"].values()):
                                        st.markdown('<div class="section-header">Skill Match Scores</div>', unsafe_allow_html=True)
                                        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                                        
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
                                        st.markdown('</div>', unsafe_allow_html=True)
                                    
                                    # Add Experience Level Gauge Chart
                                    st.markdown('<div class="section-spacing"></div>', unsafe_allow_html=True)
                                    st.markdown('<div class="section-header">Experience Level</div>', unsafe_allow_html=True)
                                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                                    
                                    # Determine experience level based on years
                                    exp_level = 0
                                    if "years_of_experience" in analysis_json:
                                        try:
                                            years_text = analysis_json["years_of_experience"]
                                            # Extract years as number
                                            years_match = re.search(r'(\d+)', years_text)
                                            if years_match:
                                                years = int(years_match.group(1))
                                                if years < 2:
                                                    exp_level = 25  # Entry level
                                                elif years < 5:
                                                    exp_level = 50  # Mid level
                                                elif years < 8:
                                                    exp_level = 75  # Senior level
                                                else:
                                                    exp_level = 100  # Expert level
                                        except:
                                            exp_level = 50  # Default to mid-level if parsing fails
                                    
                                    # Create gauge chart
                                    fig = go.Figure(go.Indicator(
                                        mode="gauge+number",
                                        value=exp_level,
                                        title={'text': "Experience Level"},
                                        gauge={
                                            'axis': {'range': [0, 100], 'tickwidth': 1},
                                            'bar': {'color': "#3B82F6"},
                                            'steps': [
                                                {'range': [0, 25], 'color': "#DBEAFE"},
                                                {'range': [25, 50], 'color': "#93C5FD"},
                                                {'range': [50, 75], 'color': "#60A5FA"},
                                                {'range': [75, 100], 'color': "#2563EB"}
                                            ],
                                            'threshold': {
                                                'line': {'color': "red", 'width': 4},
                                                'thickness': 0.75,
                                                'value': exp_level
                                            }
                                        }
                                    ))
                                    fig.update_layout(height=300)
                                    st.plotly_chart(fig, use_container_width=True)
                                    st.markdown('</div>', unsafe_allow_html=True)
                                
                                # Skills Tab
                                with tabs[1]:
                                    st.markdown('<div class="section-header">Skills</div>', unsafe_allow_html=True)
                                    if "skills" in analysis_json:
                                        skills_html = '<div style="padding: 10px;">'
                                        for skill in analysis_json["skills"]:
                                            skills_html += f'<span class="skill-tag">{skill}</span>'
                                        skills_html += '</div>'
                                        st.markdown(skills_html, unsafe_allow_html=True)
                                    
                                    # Add Skills Distribution Chart
                                    st.markdown('<div class="section-spacing"></div>', unsafe_allow_html=True)
                                    st.markdown('<div class="section-header">Skills Distribution</div>', unsafe_allow_html=True)
                                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                                    
                                    if "skills" in analysis_json and len(analysis_json["skills"]) > 0:
                                        # Categorize skills
                                        skill_categories = {
                                            "Technical": [],
                                            "Soft Skills": [],
                                            "Tools": [],
                                            "Languages": [],
                                            "Other": []
                                        }
                                        
                                        # Simple categorization logic - can be improved with more sophisticated NLP
                                        tech_keywords = ["python", "java", "javascript", "html", "css", "sql", "nosql", "react", "angular", "vue", "node", "express", "django", "flask", "spring", "algorithm", "data structure", "api", "rest", "graphql", "aws", "azure", "gcp", "cloud", "docker", "kubernetes", "ci/cd", "git", "database", "machine learning", "ai", "deep learning", "tensorflow", "pytorch", "nlp", "computer vision"]
                                        soft_keywords = ["communication", "leadership", "teamwork", "problem solving", "critical thinking", "time management", "collaboration", "adaptability", "creativity", "presentation", "negotiation", "conflict resolution", "emotional intelligence", "interpersonal", "project management", "agile", "scrum", "kanban"]
                                        tools_keywords = ["excel", "word", "powerpoint", "jira", "confluence", "slack", "trello", "asana", "photoshop", "illustrator", "figma", "sketch", "adobe", "tableau", "power bi", "looker", "jenkins", "travis", "github", "gitlab", "bitbucket"]
                                        language_keywords = ["english", "spanish", "french", "german", "chinese", "japanese", "hindi", "arabic", "russian", "portuguese", "italian"]
                                        
                                        keyword_categories = [
                                            tech_keywords,
                                            soft_keywords,
                                            tools_keywords,
                                            language_keywords
                                        ]
                                        
                                        for skill in analysis_json["skills"]:
                                            skill_lower = skill.lower()
                                            for i, keywords in enumerate(keyword_categories):
                                                if any(keyword in skill_lower for keyword in keywords):
                                                    skill_categories[list(skill_categories.keys())[i]].append(skill)
                                                    break
                                            else:
                                                skill_categories["Other"].append(skill)
                                        
                                        # Filter out empty categories
                                        skill_categories = {k: v for k, v in skill_categories.items() if v}
                                        
                                        if skill_categories:
                                            categories = list(skill_categories.keys())
                                            counts = [len(skill_categories[cat]) for cat in categories]
                                            
                                            # Create pie chart
                                            fig = go.Figure(data=[go.Pie(
                                                labels=categories,
                                                values=counts,
                                                hole=.4,
                                                marker_colors=['#3B82F6', '#10B981', '#F59E0B', '#6366F1', '#EC4899']
                                            )])
                                            fig.update_layout(
                                                title="Skills by Category",
                                                height=400
                                            )
                                            st.plotly_chart(fig, use_container_width=True)
                                    
                                    st.markdown('</div>', unsafe_allow_html=True)
                                
                                # Education Tab
                                with tabs[2]:
                                    st.markdown('<div class="section-header">Education</div>', unsafe_allow_html=True)
                                    if "education" in analysis_json:
                                        for edu in analysis_json["education"]:
                                            st.markdown(f'<div class="education-item">{edu}</div>', unsafe_allow_html=True)
                                    
                                    # Add Education Timeline
                                    st.markdown('<div class="section-spacing"></div>', unsafe_allow_html=True)
                                    st.markdown('<div class="section-header">Education Timeline</div>', unsafe_allow_html=True)
                                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                                    
                                    if "education" in analysis_json and analysis_json["education"]:
                                        # Extract years from education entries
                                        edu_years = []
                                        edu_desc = []
                                        
                                        for edu in analysis_json["education"]:
                                            # Look for year patterns like 2015-2019 or 2020
                                            year_pattern = r'(19|20)\d{2}[-–—]?(19|20)?\d{0,2}'
                                            years_found = re.findall(year_pattern, edu)
                                            
                                            if years_found:
                                                # Use the last year found as the marker
                                                year_text = years_found[-1]
                                                if isinstance(year_text, tuple):
                                                    year_text = ''.join(year_text)
                                                
                                                # Extract end year for sorting
                                                if '-' in year_text or '–' in year_text or '—' in year_text:
                                                    end_year = re.split(r'[-–—]', year_text)[-1]
                                                    if len(end_year) == 2:  # Handle cases like "2018-20"
                                                        end_year = year_text[:2] + end_year
                                                else:
                                                    end_year = year_text
                                                
                                                try:
                                                    year = int(end_year)
                                                    edu_years.append(year)
                                                    edu_desc.append(edu)
                                                except:
                                                    continue
                                        
                                        if edu_years:
                                            # Sort by year
                                            sorted_edu = sorted(zip(edu_years, edu_desc))
                                            years = [str(year) for year, _ in sorted_edu]
                                            descriptions = [desc for _, desc in sorted_edu]
                                            
                                            # Create timeline chart
                                            fig = go.Figure()
                                            
                                            for i, (year, desc) in enumerate(zip(years, descriptions)):
                                                # Truncate description if too long
                                                short_desc = desc[:50] + "..." if len(desc) > 50 else desc
                                                
                                                fig.add_trace(go.Scatter(
                                                    x=[year],
                                                    y=[i],
                                                    mode="markers+text",
                                                    marker=dict(size=20, color="#3B82F6"),
                                                    text=year,
                                                    textposition="middle right",
                                                    hoverinfo="text",
                                                    hovertext=desc,
                                                    name=short_desc
                                                ))
                                                
                                                # Add horizontal line
                                                if i > 0:
                                                    fig.add_shape(
                                                        type="line",
                                                        x0=years[i-1],
                                                        y0=i-1,
                                                        x1=year,
                                                        y1=i,
                                                        line=dict(color="#CBD5E1", width=2)
                                                    )
                                            
                                            fig.update_layout(
                                                title="Education Timeline",
                                                showlegend=True,
                                                height=100 + (len(years) * 50),
                                                xaxis=dict(title="Year"),
                                                yaxis=dict(
                                                    showticklabels=False,
                                                    showgrid=False,
                                                    zeroline=False
                                                ),
                                                plot_bgcolor='rgba(0,0,0,0)'
                                            )
                                            st.plotly_chart(fig, use_container_width=True)
                                    
                                    st.markdown('</div>', unsafe_allow_html=True)
                                
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
                                    
                                    # Add Strengths vs Improvements Chart
                                    st.markdown('<div class="section-spacing"></div>', unsafe_allow_html=True)
                                    st.markdown('<div class="section-header">Strengths vs Improvement Areas</div>', unsafe_allow_html=True)
                                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                                    
                                    if "key_strengths" in analysis_json or "areas_of_improvement" in analysis_json:
                                        # Create a more detailed and visually impactful radar chart
                                        
                                        # Extract strengths and improvements
                                        strengths = analysis_json.get("key_strengths", [])
                                        improvements = analysis_json.get("areas_of_improvement", [])
                                        
                                        # Create categories for radar chart
                                        categories = [
                                            "Technical Skills", 
                                            "Soft Skills",
                                            "Experience",
                                            "Education",
                                            "Project Work",
                                            "Leadership"
                                        ]
                                        
                                        # Score each category based on strengths and improvements
                                        # Higher score means more strengths in that area
                                        scores = [5, 5, 5, 5, 5, 5]  # Default middle scores
                                        
                                        # Keywords for each category
                                        tech_keywords = ["technical", "coding", "programming", "development", "software", "hardware", "engineering", "algorithm", "data", "analysis"]
                                        soft_keywords = ["communication", "teamwork", "collaboration", "interpersonal", "adaptability", "problem-solving", "critical thinking", "creativity"]
                                        exp_keywords = ["experience", "work history", "professional", "industry", "career", "job", "role", "position"]
                                        edu_keywords = ["education", "degree", "qualification", "academic", "university", "college", "school", "certification"]
                                        project_keywords = ["project", "portfolio", "implementation", "development", "application", "system", "solution"]
                                        leadership_keywords = ["leadership", "management", "team lead", "supervision", "direction", "guidance", "mentoring", "strategic"]
                                        
                                        keyword_categories = [
                                            tech_keywords,
                                            soft_keywords,
                                            exp_keywords,
                                            edu_keywords,
                                            project_keywords,
                                            leadership_keywords
                                        ]
                                        
                                        # Analyze strengths and improvements to adjust scores
                                        for i, keywords in enumerate(keyword_categories):
                                            # Check strengths that match this category
                                            strength_matches = sum(1 for s in strengths if any(k in s.lower() for k in keywords))
                                            
                                            # Check improvements that match this category
                                            improvement_matches = sum(1 for imp in improvements if any(k in imp.lower() for k in keywords))
                                            
                                            # Adjust score: increase for strengths, decrease for improvements
                                            # Scale from 0-10, with 5 as neutral
                                            adjustment = min(5, strength_matches) - min(5, improvement_matches)
                                            scores[i] = max(0, min(10, 5 + adjustment))
                                        
                                        # Create radar chart
                                        fig = go.Figure()
                                        
                                        # Add strengths trace
                                        fig.add_trace(go.Scatterpolar(
                                            r=scores,
                                            theta=categories,
                                            fill='toself',
                                            name='Profile Strength',
                                            line_color='#10B981',
                                            fillcolor='rgba(16, 185, 129, 0.2)'
                                        ))
                                        
                                        # Add baseline trace for reference
                                        fig.add_trace(go.Scatterpolar(
                                            r=[5, 5, 5, 5, 5, 5],
                                            theta=categories,
                                            fill='toself',
                                            name='Baseline',
                                            line_color='#94A3B8',
                                            fillcolor='rgba(148, 163, 184, 0.1)'
                                        ))
                                        
                                        # Configure layout
                                        fig.update_layout(
                                            polar=dict(
                                                radialaxis=dict(
                                                    visible=True,
                                                    range=[0, 10]
                                                )
                                            ),
                                            title="Resume Strength Profile",
                                            height=450,
                                            showlegend=True
                                        )
                                        
                                        # Display the chart
                                        st.plotly_chart(fig, use_container_width=True)
                                        
                                        # Add a small explanation
                                        st.markdown("""
                                        <div style="font-size: 0.9rem; color: #64748B; padding: 0.8rem; background-color: #F8FAFC; border-radius: 5px; margin-top: 1rem;">
                                        <strong>How to interpret:</strong> This radar chart shows the strength profile across different categories. 
                                        Areas extending beyond the baseline indicate strengths, while areas inside the baseline suggest potential areas for improvement.
                                        </div>
                                        """, unsafe_allow_html=True)
                                    
                                    st.markdown('</div>', unsafe_allow_html=True)
                                
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
