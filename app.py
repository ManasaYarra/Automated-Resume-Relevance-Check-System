import streamlit as st
import pandas as pd
import os
from datetime import datetime
import io
from typing import Optional, Dict, Any

from database import DatabaseManager
from document_parser import DocumentParser
from ai_analyzer import AIAnalyzer
from scoring_engine import ScoringEngine
from models import JobDescription, Resume, AnalysisResult
from utils import validate_file_type, format_score, get_verdict_color

# Initialize components
@st.cache_resource
def initialize_components():
    db = DatabaseManager()
    parser = DocumentParser()
    ai_analyzer = AIAnalyzer()
    scoring_engine = ScoringEngine()
    return db, parser, ai_analyzer, scoring_engine

def main():
    st.set_page_config(
        page_title="AI Resume Matcher",
        page_icon="🎯",
        layout="wide"
    )
    import streamlit as st

st.title("Test Streamlit app")

st.write("If you see this message, Streamlit started correctly!")

print("Starting app.py")
import streamlit as st
st.write("App is starting...")

    import streamlit as st

st.title("Automated Resume Relevance Check System")
st.write("App is running successfully!")

st.title("🎯 AI-Powered Resume Matching System")
st.markdown("**Intelligent resume-job description matching for placement teams**")
    
    # Initialize components
    db, parser, ai_analyzer, scoring_engine = initialize_components()
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Select Page",
        ["Job Description Upload", "Resume Analysis", "Dashboard", "Search Results"]
    )
    
    if page == "Job Description Upload":
        job_description_upload_page(db, parser)
    elif page == "Resume Analysis":
        resume_analysis_page(db, parser, ai_analyzer, scoring_engine)
    elif page == "Dashboard":
        dashboard_page(db)
    elif page == "Search Results":
        search_results_page(db)

def job_description_upload_page(db: DatabaseManager, parser: DocumentParser):
    st.header("📄 Job Description Upload")
    
    with st.form("jd_upload_form"):
        st.subheader("Upload Job Description")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose a job description file",
            type=['pdf', 'docx', 'txt'],
            help="Upload PDF, DOCX, or TXT files"
        )
        
        # Manual input fields
        col1, col2 = st.columns(2)
        with col1:
            job_title = st.text_input("Job Title*", placeholder="e.g., Software Engineer")
            company_name = st.text_input("Company Name", placeholder="e.g., TechCorp Inc.")
            location = st.text_input("Location", placeholder="e.g., New York, NY")
        
        with col2:
            experience_level = st.selectbox(
                "Experience Level",
                ["Entry Level", "Mid Level", "Senior Level", "Executive"]
            )
            department = st.text_input("Department", placeholder="e.g., Engineering")
            employment_type = st.selectbox(
                "Employment Type",
                ["Full-time", "Part-time", "Contract", "Internship"]
            )
        
        # Additional details
        st.subheader("Additional Requirements")
        must_have_skills = st.text_area(
            "Must-have Skills (comma-separated)",
            placeholder="e.g., Python, React, SQL, Git"
        )
        nice_to_have_skills = st.text_area(
            "Nice-to-have Skills (comma-separated)",
            placeholder="e.g., Docker, AWS, Machine Learning"
        )
        
        submit_button = st.form_submit_button("Upload Job Description")
        
        if submit_button:
            if not job_title:
                st.error("Job title is required!")
                return
            
            try:
                # Parse uploaded file if provided
                job_description_text = ""
                if uploaded_file is not None:
                    if validate_file_type(uploaded_file.name, ['pdf', 'docx', 'txt']):
                        job_description_text = parser.extract_text_from_file(uploaded_file)
                    else:
                        st.error("Invalid file type. Please upload PDF, DOCX, or TXT files.")
                        return
                
                # Create job description object
                jd = JobDescription(
                    title=job_title,
                    company=company_name,
                    location=location,
                    experience_level=experience_level,
                    department=department,
                    employment_type=employment_type,
                    description=job_description_text,
                    must_have_skills=[skill.strip() for skill in must_have_skills.split(',') if skill.strip()],
                    nice_to_have_skills=[skill.strip() for skill in nice_to_have_skills.split(',') if skill.strip()]
                )
                
                # Save to database
                jd_id = db.save_job_description(jd)
                
                st.success(f"✅ Job description saved successfully! (ID: {jd_id})")
                st.info("You can now analyze resumes against this job description in the Resume Analysis page.")
                
            except Exception as e:
                st.error(f"Error saving job description: {str(e)}")

def resume_analysis_page(db: DatabaseManager, parser: DocumentParser, 
                        ai_analyzer: AIAnalyzer, scoring_engine: ScoringEngine):
    st.header("🔍 Resume Analysis")
    
    # Select job description
    job_descriptions = db.get_all_job_descriptions()
    if not job_descriptions:
        st.warning("⚠️ No job descriptions found. Please upload a job description first.")
        return
    
    jd_options = {f"{jd['title']} - {jd['company']} (ID: {jd['id']})": jd['id'] 
                  for jd in job_descriptions}
    
    selected_jd_key = st.selectbox("Select Job Description", list(jd_options.keys()))
    selected_jd_id = jd_options[selected_jd_key]
    
    # Resume upload
    with st.form("resume_analysis_form"):
        st.subheader("Upload Resume for Analysis")
        
        uploaded_resume = st.file_uploader(
            "Choose a resume file",
            type=['pdf', 'docx'],
            help="Upload PDF or DOCX files"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            candidate_name = st.text_input("Candidate Name", placeholder="e.g., John Doe")
            candidate_email = st.text_input("Candidate Email", placeholder="e.g., john@example.com")
        
        with col2:
            candidate_phone = st.text_input("Phone Number", placeholder="e.g., +1-555-0123")
            candidate_location = st.text_input("Candidate Location", placeholder="e.g., San Francisco, CA")
        
        analyze_button = st.form_submit_button("🚀 Analyze Resume")
        
        if analyze_button:
            if uploaded_resume is None:
                st.error("Please upload a resume file!")
                return
            
            if not candidate_name or not candidate_email:
                st.error("Candidate name and email are required!")
                return
            
            try:
                with st.spinner("Analyzing resume... This may take a few moments."):
                    # Parse resume
                    resume_text = parser.extract_text_from_file(uploaded_resume)
                    
                    # Get job description
                    jd_data = db.get_job_description(selected_jd_id)
                    jd = JobDescription(**jd_data)
                    
                    # Create resume object
                    resume = Resume(
                        candidate_name=candidate_name,
                        candidate_email=candidate_email,
                        candidate_phone=candidate_phone,
                        candidate_location=candidate_location,
                        content=resume_text,
                        filename=uploaded_resume.name
                    )
                    
                    # Perform AI analysis
                    ai_analysis = ai_analyzer.analyze_resume_job_match(resume, jd)
                    
                    # Calculate scores
                    scores = scoring_engine.calculate_hybrid_score(resume, jd, ai_analysis)
                    
                    # Create analysis result
                    result = AnalysisResult(
                        resume=resume,
                        job_description=jd,
                        relevance_score=scores['final_score'],
                        keyword_score=scores['keyword_score'],
                        semantic_score=scores['semantic_score'],
                        missing_skills=ai_analysis.get('missing_skills', []),
                        missing_qualifications=ai_analysis.get('missing_qualifications', []),
                        verdict=scores['verdict'],
                        suggestions=ai_analysis.get('suggestions', []),
                        ai_reasoning=ai_analysis.get('reasoning', '')
                    )
                    
                    # Save to database
                    result_id = db.save_analysis_result(result, selected_jd_id)
                    
                    # Display results
                    display_analysis_results(result)
                    
                    st.success(f"✅ Analysis completed and saved! (Result ID: {result_id})")
                    
            except Exception as e:
                st.error(f"Error analyzing resume: {str(e)}")

def display_analysis_results(result: AnalysisResult):
    st.subheader("📊 Analysis Results")
    
    # Score overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Overall Score",
            f"{result.relevance_score}%",
            delta=None
        )
    
    with col2:
        st.metric(
            "Keyword Match",
            f"{result.keyword_score}%"
        )
    
    with col3:
        st.metric(
            "Semantic Match",
            f"{result.semantic_score}%"
        )
    
    with col4:
        verdict_color = get_verdict_color(result.verdict)
        st.markdown(f"**Verdict:** <span style='color: {verdict_color}'>{result.verdict}</span>", 
                   unsafe_allow_html=True)
    
    # Detailed breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("❌ Missing Elements")
        
        if result.missing_skills:
            st.write("**Missing Skills:**")
            for skill in result.missing_skills:
                st.write(f"• {skill}")
        
        if result.missing_qualifications:
            st.write("**Missing Qualifications:**")
            for qual in result.missing_qualifications:
                st.write(f"• {qual}")
        
        if not result.missing_skills and not result.missing_qualifications:
            st.write("✅ No significant missing elements found!")
    
    with col2:
        st.subheader("💡 Improvement Suggestions")
        
        if result.suggestions:
            for i, suggestion in enumerate(result.suggestions, 1):
                st.write(f"{i}. {suggestion}")
        else:
            st.write("✅ No specific suggestions at this time.")
    
    # AI Reasoning
    if result.ai_reasoning:
        st.subheader("🤖 AI Analysis")
        st.write(result.ai_reasoning)

def dashboard_page(db: DatabaseManager):
    st.header("📈 Dashboard")
    
    # Summary statistics
    stats = db.get_dashboard_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Job Descriptions", stats.get('total_jobs', 0))
    with col2:
        st.metric("Total Resumes Analyzed", stats.get('total_resumes', 0))
    with col3:
        st.metric("High Scoring Matches", stats.get('high_score_matches', 0))
    with col4:
        st.metric("Average Score", f"{stats.get('avg_score', 0):.1f}%")
    
    # Recent analyses
    st.subheader("📋 Recent Analyses")
    recent_results = db.get_recent_analysis_results(limit=10)
    
    if recent_results:
        df = pd.DataFrame(recent_results)
        df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
        
        # Format the dataframe for display
        display_df = df[['candidate_name', 'job_title', 'company', 'relevance_score', 'verdict', 'created_at']].copy()
        display_df.columns = ['Candidate', 'Job Title', 'Company', 'Score', 'Verdict', 'Date']
        
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("No analyses found.")

def search_results_page(db: DatabaseManager):
    st.header("🔍 Search & Filter Results")
    
    # Search filters
    with st.form("search_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            job_title_filter = st.text_input("Job Title")
            company_filter = st.text_input("Company")
        
        with col2:
            min_score = st.slider("Minimum Score", 0, 100, 0)
            verdict_filter = st.multiselect(
                "Verdict",
                ["High", "Medium", "Low"]
            )
        
        with col3:
            location_filter = st.text_input("Location")
            date_from = st.date_input("From Date", value=None)
        
        search_button = st.form_submit_button("🔍 Search")
    
    if search_button or st.session_state.get('auto_search', False):
        # Build search criteria
        search_criteria = {}
        if job_title_filter:
            search_criteria['job_title'] = job_title_filter
        if company_filter:
            search_criteria['company'] = company_filter
        if min_score > 0:
            search_criteria['min_score'] = min_score
        if verdict_filter:
            search_criteria['verdict'] = verdict_filter
        if location_filter:
            search_criteria['location'] = location_filter
        if date_from:
            search_criteria['date_from'] = date_from
        
        # Search results
        results = db.search_analysis_results(search_criteria)
        
        if results:
            st.subheader(f"📋 Search Results ({len(results)} found)")
            
            # Display results
            for result in results:
                with st.expander(
                    f"{result['candidate_name']} - {result['job_title']} ({result['relevance_score']}%)"
                ):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Email:** {result['candidate_email']}")
                        st.write(f"**Phone:** {result.get('candidate_phone', 'N/A')}")
                        st.write(f"**Location:** {result.get('candidate_location', 'N/A')}")
                        st.write(f"**Company:** {result['company']}")
                    
                    with col2:
                        st.write(f"**Score:** {result['relevance_score']}%")
                        st.write(f"**Verdict:** {result['verdict']}")
                        st.write(f"**Date:** {result['created_at']}")
                    
                    if result.get('missing_skills'):
                        st.write(f"**Missing Skills:** {', '.join(result['missing_skills'])}")
                    
                    if result.get('suggestions'):
                        st.write("**Suggestions:**")
                        for suggestion in result['suggestions'][:3]:  # Show first 3
                            st.write(f"• {suggestion}")
        else:
            st.info("No results found matching your criteria.")

if __name__ == "__main__":
    main()
