import os
import json
import numpy as np
from typing import Dict, List, Optional, Any
from openai import OpenAI

from models import Resume, JobDescription

class AIAnalyzer:
    def __init__(self):
        self.openai_client = OpenAI(
            api_key=os.getenv('OPENAI_API_KEY', 'your-openai-api-key')
        )
        # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
        # do not change this unless explicitly requested by the user
        self.model = "gpt-5"
    
    def analyze_resume_job_match(self, resume: Resume, job_description: JobDescription) -> Dict[str, Any]:
        """
        Perform comprehensive AI-powered analysis of resume-job match
        """
        try:
            # Generate embeddings for semantic similarity
            resume_embedding = self._get_embedding(resume.content)
            jd_embedding = self._get_embedding(job_description.description)
            
            # Calculate semantic similarity
            semantic_similarity = self._calculate_cosine_similarity(
                resume_embedding, jd_embedding
            )
            
            # Perform detailed LLM analysis
            detailed_analysis = self._perform_detailed_analysis(resume, job_description)
            
            # Combine results
            analysis_result = {
                'semantic_similarity': semantic_similarity,
                'missing_skills': detailed_analysis.get('missing_skills', []),
                'missing_qualifications': detailed_analysis.get('missing_qualifications', []),
                'matching_skills': detailed_analysis.get('matching_skills', []),
                'experience_assessment': detailed_analysis.get('experience_assessment', ''),
                'education_assessment': detailed_analysis.get('education_assessment', ''),
                'suggestions': detailed_analysis.get('suggestions', []),
                'reasoning': detailed_analysis.get('reasoning', ''),
                'strengths': detailed_analysis.get('strengths', []),
                'weaknesses': detailed_analysis.get('weaknesses', [])
            }
            
            return analysis_result
            
        except Exception as e:
            raise Exception(f"AI analysis failed: {str(e)}")
    
    def _get_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI's embedding model"""
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-large",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"Failed to generate embedding: {str(e)}")
    
    def _calculate_cosine_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
        except Exception as e:
            raise Exception(f"Failed to calculate cosine similarity: {str(e)}")
    
    def _perform_detailed_analysis(self, resume: Resume, job_description: JobDescription) -> Dict[str, Any]:
        """Perform detailed LLM-based analysis of resume-job match"""
        try:
            # Prepare the analysis prompt
            analysis_prompt = self._create_analysis_prompt(resume, job_description)
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert HR analyst and resume reviewer. 
                        Your task is to analyze how well a candidate's resume matches a job description.
                        Provide detailed, actionable insights and maintain objectivity.
                        Respond with valid JSON in the specified format."""
                    },
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            if content is None:
                raise Exception("No content received from AI model")
            analysis_result = json.loads(content)
            return analysis_result
            
        except Exception as e:
            raise Exception(f"Detailed LLM analysis failed: {str(e)}")
    
    def _create_analysis_prompt(self, resume: Resume, job_description: JobDescription) -> str:
        """Create comprehensive analysis prompt for LLM"""
        
        # Format skills for better analysis
        must_have_skills = ', '.join(job_description.must_have_skills) if job_description.must_have_skills else "Not specified"
        nice_to_have_skills = ', '.join(job_description.nice_to_have_skills) if job_description.nice_to_have_skills else "Not specified"
        
        prompt = f"""
Analyze the following resume against the job description and provide a comprehensive assessment.

JOB DESCRIPTION:
Title: {job_description.title}
Company: {job_description.company or 'Not specified'}
Experience Level: {job_description.experience_level or 'Not specified'}
Employment Type: {job_description.employment_type or 'Not specified'}

Must-have Skills: {must_have_skills}
Nice-to-have Skills: {nice_to_have_skills}

Job Description Content:
{job_description.description}

RESUME:
Candidate: {resume.candidate_name}
Location: {resume.candidate_location or 'Not specified'}

Resume Content:
{resume.content}

Please provide a detailed analysis in the following JSON format:
{{
    "missing_skills": ["skill1", "skill2"],
    "missing_qualifications": ["qualification1", "qualification2"],
    "matching_skills": ["skill1", "skill2"],
    "experience_assessment": "Brief assessment of relevant experience",
    "education_assessment": "Brief assessment of educational background",
    "suggestions": [
        "Specific suggestion 1",
        "Specific suggestion 2",
        "Specific suggestion 3"
    ],
    "reasoning": "Detailed explanation of the overall assessment",
    "strengths": ["strength1", "strength2"],
    "weaknesses": ["weakness1", "weakness2"]
}}

Focus on:
1. Technical skills alignment with job requirements
2. Experience level and relevance
3. Educational background fit
4. Missing critical skills or qualifications
5. Actionable improvement suggestions
6. Overall candidate potential for this role

Be specific and constructive in your assessment.
"""
        return prompt
    
    def generate_improvement_suggestions(self, resume: Resume, job_description: JobDescription, 
                                       analysis_result: Dict[str, Any]) -> List[str]:
        """Generate specific improvement suggestions for the candidate"""
        try:
            suggestions_prompt = f"""
Based on the resume analysis, generate 5 specific, actionable suggestions for the candidate to improve their match for this role.

Job Title: {job_description.title}
Missing Skills: {', '.join(analysis_result.get('missing_skills', []))}
Missing Qualifications: {', '.join(analysis_result.get('missing_qualifications', []))}
Weaknesses: {', '.join(analysis_result.get('weaknesses', []))}

Current Resume Content (first 500 chars):
{resume.content[:500]}...

Provide suggestions in JSON format:
{{
    "suggestions": [
        "Specific actionable suggestion 1",
        "Specific actionable suggestion 2",
        "Specific actionable suggestion 3",
        "Specific actionable suggestion 4",
        "Specific actionable suggestion 5"
    ]
}}

Each suggestion should be:
- Specific and actionable
- Related to the missing skills or weaknesses
- Achievable within 3-6 months
- Directly relevant to the job requirements
"""
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a career counselor providing specific improvement advice."
                    },
                    {
                        "role": "user",
                        "content": suggestions_prompt
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            if content is None:
                raise Exception("No content received from AI model")
            result = json.loads(content)
            return result.get('suggestions', [])
            
        except Exception as e:
            # Fallback to basic suggestions if AI fails
            return [
                "Consider acquiring the missing technical skills through online courses",
                "Gain practical experience with the required technologies through projects",
                "Update resume to highlight relevant experience more prominently",
                "Consider obtaining relevant certifications in the required skill areas",
                "Network with professionals in the industry to gain insights and opportunities"
            ]
    
    def assess_candidate_potential(self, resume: Resume, job_description: JobDescription) -> Dict[str, Any]:
        """Assess overall candidate potential and cultural fit"""
        try:
            potential_prompt = f"""
Assess the candidate's potential for growth and success in this role beyond just current skills.

Job: {job_description.title} at {job_description.company or 'the company'}
Experience Level Required: {job_description.experience_level or 'Not specified'}

Resume Content:
{resume.content}

Evaluate and respond in JSON format:
{{
    "growth_potential": "High/Medium/Low",
    "learning_ability_indicators": ["indicator1", "indicator2"],
    "cultural_fit_assessment": "Assessment of potential cultural fit",
    "adaptability_score": 85,
    "recommended_onboarding_focus": ["area1", "area2"],
    "long_term_potential": "Assessment of long-term potential"
}}

Consider:
- Evidence of continuous learning
- Career progression patterns
- Project complexity and impact
- Leadership or initiative indicators
- Technical depth vs. breadth
- Problem-solving capabilities
"""
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a senior HR strategist assessing candidate potential."
                    },
                    {
                        "role": "user",
                        "content": potential_prompt
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            if content is None:
                raise Exception("No content received from AI model")
            return json.loads(content)
            
        except Exception as e:
            # Return basic assessment if AI fails
            return {
                "growth_potential": "Medium",
                "learning_ability_indicators": ["Professional experience", "Educational background"],
                "cultural_fit_assessment": "Requires further evaluation during interview process",
                "adaptability_score": 70,
                "recommended_onboarding_focus": ["Technical skills development", "Team integration"],
                "long_term_potential": "Shows promise for growth with proper development"
            }
