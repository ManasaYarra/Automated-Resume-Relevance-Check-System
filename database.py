import os
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

from models import JobDescription, Resume, AnalysisResult

class DatabaseManager:
    def __init__(self):
        self.connection_params = {
            'host': os.getenv('PGHOST', 'localhost'),
            'port': os.getenv('PGPORT', '5432'),
            'database': os.getenv('PGDATABASE', 'resume_matcher'),
            'user': os.getenv('PGUSER', 'postgres'),
            'password': os.getenv('PGPASSWORD', 'password')
        }
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        try:
            conn = psycopg2.connect(
                host=self.connection_params['host'],
                port=self.connection_params['port'],
                database=self.connection_params['database'],
                user=self.connection_params['user'],
                password=self.connection_params['password']
            )
            return conn
        except psycopg2.Error as e:
            raise Exception(f"Database connection failed: {str(e)}")
    
    def init_database(self):
        """Initialize database tables"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Create job_descriptions table
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS job_descriptions (
                            id SERIAL PRIMARY KEY,
                            title VARCHAR(255) NOT NULL,
                            company VARCHAR(255),
                            location VARCHAR(255),
                            experience_level VARCHAR(50),
                            department VARCHAR(100),
                            employment_type VARCHAR(50),
                            description TEXT,
                            must_have_skills TEXT[],
                            nice_to_have_skills TEXT[],
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # Create resumes table
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS resumes (
                            id SERIAL PRIMARY KEY,
                            candidate_name VARCHAR(255) NOT NULL,
                            candidate_email VARCHAR(255) NOT NULL,
                            candidate_phone VARCHAR(50),
                            candidate_location VARCHAR(255),
                            content TEXT NOT NULL,
                            filename VARCHAR(255),
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # Create analysis_results table
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS analysis_results (
                            id SERIAL PRIMARY KEY,
                            job_description_id INTEGER REFERENCES job_descriptions(id),
                            resume_id INTEGER REFERENCES resumes(id),
                            relevance_score INTEGER NOT NULL,
                            keyword_score INTEGER,
                            semantic_score INTEGER,
                            missing_skills TEXT[],
                            missing_qualifications TEXT[],
                            verdict VARCHAR(20) NOT NULL,
                            suggestions TEXT[],
                            ai_reasoning TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # Create indexes for better performance
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_job_descriptions_title 
                        ON job_descriptions(title)
                    """)
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_job_descriptions_company 
                        ON job_descriptions(company)
                    """)
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_resumes_email 
                        ON resumes(candidate_email)
                    """)
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_analysis_results_score 
                        ON analysis_results(relevance_score)
                    """)
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_analysis_results_verdict 
                        ON analysis_results(verdict)
                    """)
                    
                conn.commit()
        except Exception as e:
            raise Exception(f"Database initialization failed: {str(e)}")
    
    def save_job_description(self, jd: JobDescription) -> int:
        """Save job description to database"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO job_descriptions 
                        (title, company, location, experience_level, department, 
                         employment_type, description, must_have_skills, nice_to_have_skills)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (
                        jd.title, jd.company, jd.location, jd.experience_level,
                        jd.department, jd.employment_type, jd.description,
                        jd.must_have_skills, jd.nice_to_have_skills
                    ))
                    job_id = cursor.fetchone()[0]
                    conn.commit()
                    return job_id
        except Exception as e:
            raise Exception(f"Failed to save job description: {str(e)}")
    
    def save_resume(self, resume: Resume) -> int:
        """Save resume to database"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO resumes 
                        (candidate_name, candidate_email, candidate_phone, 
                         candidate_location, content, filename)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (
                        resume.candidate_name, resume.candidate_email,
                        resume.candidate_phone, resume.candidate_location,
                        resume.content, resume.filename
                    ))
                    resume_id = cursor.fetchone()[0]
                    conn.commit()
                    return resume_id
        except Exception as e:
            raise Exception(f"Failed to save resume: {str(e)}")
    
    def save_analysis_result(self, result: AnalysisResult, job_description_id: int) -> int:
        """Save analysis result to database"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # First save the resume
                    resume_id = self.save_resume(result.resume)
                    
                    # Then save the analysis result
                    cursor.execute("""
                        INSERT INTO analysis_results 
                        (job_description_id, resume_id, relevance_score, keyword_score,
                         semantic_score, missing_skills, missing_qualifications,
                         verdict, suggestions, ai_reasoning)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (
                        job_description_id, resume_id, result.relevance_score,
                        result.keyword_score, result.semantic_score,
                        result.missing_skills, result.missing_qualifications,
                        result.verdict, result.suggestions, result.ai_reasoning
                    ))
                    result_id = cursor.fetchone()[0]
                    conn.commit()
                    return result_id
        except Exception as e:
            raise Exception(f"Failed to save analysis result: {str(e)}")
    
    def get_job_description(self, job_id: int) -> Dict[str, Any]:
        """Get job description by ID"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT * FROM job_descriptions WHERE id = %s
                    """, (job_id,))
                    result = cursor.fetchone()
                    if result:
                        return dict(result)
                    else:
                        raise Exception(f"Job description with ID {job_id} not found")
        except Exception as e:
            raise Exception(f"Failed to get job description: {str(e)}")
    
    def get_all_job_descriptions(self) -> List[Dict[str, Any]]:
        """Get all job descriptions"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT id, title, company, location, created_at 
                        FROM job_descriptions 
                        ORDER BY created_at DESC
                    """)
                    return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            raise Exception(f"Failed to get job descriptions: {str(e)}")
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Total job descriptions
                    cursor.execute("SELECT COUNT(*) FROM job_descriptions")
                    total_jobs = cursor.fetchone()[0]
                    
                    # Total resumes analyzed
                    cursor.execute("SELECT COUNT(*) FROM analysis_results")
                    total_resumes = cursor.fetchone()[0]
                    
                    # High scoring matches (>= 70%)
                    cursor.execute("""
                        SELECT COUNT(*) FROM analysis_results 
                        WHERE relevance_score >= 70
                    """)
                    high_score_matches = cursor.fetchone()[0]
                    
                    # Average score
                    cursor.execute("""
                        SELECT AVG(relevance_score) FROM analysis_results
                    """)
                    avg_score = cursor.fetchone()[0] or 0
                    
                    return {
                        'total_jobs': total_jobs,
                        'total_resumes': total_resumes,
                        'high_score_matches': high_score_matches,
                        'avg_score': float(avg_score)
                    }
        except Exception as e:
            raise Exception(f"Failed to get dashboard stats: {str(e)}")
    
    def get_recent_analysis_results(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent analysis results"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT 
                            ar.id,
                            r.candidate_name,
                            r.candidate_email,
                            jd.title as job_title,
                            jd.company,
                            ar.relevance_score,
                            ar.verdict,
                            ar.created_at
                        FROM analysis_results ar
                        JOIN resumes r ON ar.resume_id = r.id
                        JOIN job_descriptions jd ON ar.job_description_id = jd.id
                        ORDER BY ar.created_at DESC
                        LIMIT %s
                    """, (limit,))
                    return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            raise Exception(f"Failed to get recent analysis results: {str(e)}")
    
    def search_analysis_results(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search analysis results with filters"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # Build dynamic query
                    where_conditions = []
                    params = []
                    
                    if criteria.get('job_title'):
                        where_conditions.append("jd.title ILIKE %s")
                        params.append(f"%{criteria['job_title']}%")
                    
                    if criteria.get('company'):
                        where_conditions.append("jd.company ILIKE %s")
                        params.append(f"%{criteria['company']}%")
                    
                    if criteria.get('min_score'):
                        where_conditions.append("ar.relevance_score >= %s")
                        params.append(criteria['min_score'])
                    
                    if criteria.get('verdict'):
                        verdict_list = criteria['verdict']
                        placeholders = ','.join(['%s'] * len(verdict_list))
                        where_conditions.append(f"ar.verdict IN ({placeholders})")
                        params.extend(verdict_list)
                    
                    if criteria.get('location'):
                        where_conditions.append("""
                            (r.candidate_location ILIKE %s OR jd.location ILIKE %s)
                        """)
                        location_param = f"%{criteria['location']}%"
                        params.extend([location_param, location_param])
                    
                    if criteria.get('date_from'):
                        where_conditions.append("ar.created_at >= %s")
                        params.append(criteria['date_from'])
                    
                    where_clause = ""
                    if where_conditions:
                        where_clause = "WHERE " + " AND ".join(where_conditions)
                    
                    query = f"""
                        SELECT 
                            ar.id,
                            r.candidate_name,
                            r.candidate_email,
                            r.candidate_phone,
                            r.candidate_location,
                            jd.title as job_title,
                            jd.company,
                            ar.relevance_score,
                            ar.verdict,
                            ar.missing_skills,
                            ar.suggestions,
                            ar.created_at
                        FROM analysis_results ar
                        JOIN resumes r ON ar.resume_id = r.id
                        JOIN job_descriptions jd ON ar.job_description_id = jd.id
                        {where_clause}
                        ORDER BY ar.relevance_score DESC, ar.created_at DESC
                    """
                    
                    cursor.execute(query, params)
                    return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            raise Exception(f"Failed to search analysis results: {str(e)}")
