import re
import math
from typing import Dict, List, Tuple, Any
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:
    TfidfVectorizer = None
    cosine_similarity = None

try:
    from fuzzywuzzy import fuzz, process
except ImportError:
    fuzz = None
    process = None

from models import Resume, JobDescription

class ScoringEngine:
    def __init__(self):
        if TfidfVectorizer is not None:
            self.tfidf_vectorizer = TfidfVectorizer(
                stop_words='english',
                ngram_range=(1, 2),
                max_features=1000
            )
        else:
            self.tfidf_vectorizer = None
        
        # Scoring weights
        self.weights = {
            'keyword_score': 0.4,      # 40% weight for keyword matching
            'semantic_score': 0.35,    # 35% weight for semantic similarity
            'skill_match': 0.15,       # 15% weight for skill matching
            'experience_match': 0.1    # 10% weight for experience matching
        }
    
    def calculate_hybrid_score(self, resume: Resume, job_description: JobDescription, 
                             ai_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive hybrid score combining multiple factors"""
        try:
            # Calculate individual scores
            keyword_score = self._calculate_keyword_score(resume, job_description)
            semantic_score = self._calculate_semantic_score(ai_analysis)
            skill_match_score = self._calculate_skill_match_score(resume, job_description)
            experience_score = self._calculate_experience_score(resume, job_description)
            
            # Calculate weighted final score
            final_score = (
                keyword_score * self.weights['keyword_score'] +
                semantic_score * self.weights['semantic_score'] +
                skill_match_score * self.weights['skill_match'] +
                experience_score * self.weights['experience_match']
            )
            
            # Ensure score is within 0-100 range
            final_score = max(0, min(100, round(final_score)))
            
            # Determine verdict based on score
            verdict = self._determine_verdict(final_score)
            
            return {
                'final_score': final_score,
                'keyword_score': round(keyword_score),
                'semantic_score': round(semantic_score),
                'skill_match_score': round(skill_match_score),
                'experience_score': round(experience_score),
                'verdict': verdict,
                'score_breakdown': {
                    'keyword_weight': self.weights['keyword_score'],
                    'semantic_weight': self.weights['semantic_score'],
                    'skill_weight': self.weights['skill_match'],
                    'experience_weight': self.weights['experience_match']
                }
            }
            
        except Exception as e:
            raise Exception(f"Score calculation failed: {str(e)}")
    
    def _calculate_keyword_score(self, resume: Resume, job_description: JobDescription) -> float:
        """Calculate keyword matching score using TF-IDF and fuzzy matching"""
        try:
            # Prepare texts
            resume_text = resume.content.lower()
            jd_text = job_description.description.lower()
            
            # Combine must-have and nice-to-have skills for analysis
            all_required_skills = (
                (job_description.must_have_skills or []) + 
                (job_description.nice_to_have_skills or [])
            )
            
            # Calculate TF-IDF similarity
            tfidf_score = self._calculate_tfidf_similarity(resume_text, jd_text)
            
            # Calculate keyword presence score
            keyword_score = self._calculate_keyword_presence(resume_text, jd_text)
            
            # Calculate skill-specific matching
            skill_score = self._calculate_skill_keyword_match(resume_text, all_required_skills)
            
            # Combine scores with weights
            combined_score = (
                tfidf_score * 0.4 +
                keyword_score * 0.3 +
                skill_score * 0.3
            ) * 100
            
            return min(100, combined_score)
            
        except Exception as e:
            return 0.0
    
    def _calculate_tfidf_similarity(self, resume_text: str, jd_text: str) -> float:
        """Calculate TF-IDF cosine similarity between resume and job description"""
        try:
            if self.tfidf_vectorizer is None or cosine_similarity is None:
                return 0.0
            
            # Fit TF-IDF vectorizer and transform texts
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([resume_text, jd_text])
            
            # Calculate cosine similarity
            similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            
            return float(similarity_matrix[0][0])
            
        except Exception as e:
            return 0.0
    
    def _calculate_keyword_presence(self, resume_text: str, jd_text: str) -> float:
        """Calculate keyword presence score"""
        try:
            # Extract important keywords from job description
            jd_keywords = self._extract_important_keywords(jd_text)
            
            if not jd_keywords:
                return 0.0
            
            # Count keyword matches in resume
            matches = 0
            total_keywords = len(jd_keywords)
            
            for keyword in jd_keywords:
                # Check for exact match or fuzzy match
                if keyword in resume_text:
                    matches += 1
                elif process is not None and fuzz is not None:
                    # Use fuzzy matching for partial matches
                    best_match = process.extractOne(
                        keyword, 
                        resume_text.split(),
                        scorer=fuzz.partial_ratio
                    )
                    if best_match and best_match[1] >= 80:  # 80% similarity threshold
                        matches += 0.7  # Partial credit for fuzzy matches
            
            return matches / total_keywords if total_keywords > 0 else 0.0
            
        except Exception as e:
            return 0.0
    
    def _extract_important_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        # Remove common stop words and extract meaningful terms
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        
        # Filter out very short words and common terms
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before',
            'after', 'above', 'below', 'between', 'among', 'is', 'are', 'was',
            'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does',
            'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
            'can', 'shall', 'this', 'that', 'these', 'those'
        }
        
        keywords = [
            word for word in words 
            if len(word) > 3 and word not in stop_words
        ]
        
        # Return unique keywords
        return list(set(keywords))
    
    def _calculate_skill_keyword_match(self, resume_text: str, required_skills: List[str]) -> float:
        """Calculate skill-specific keyword matching"""
        if not required_skills:
            return 1.0  # If no specific skills required, give full score
        
        matches = 0
        total_skills = len(required_skills)
        
        for skill in required_skills:
            skill_lower = skill.lower().strip()
            
            # Check for exact match
            if skill_lower in resume_text:
                matches += 1
            else:
                # Check for fuzzy match
                skill_words = skill_lower.split()
                resume_words = resume_text.split()
                
                # Check if all words in skill are present in resume
                word_matches = sum(1 for word in skill_words if word in resume_words)
                if word_matches == len(skill_words):
                    matches += 0.8  # High score for all words present
                elif word_matches > 0:
                    matches += 0.4  # Partial score for some words present
        
        return matches / total_skills if total_skills > 0 else 1.0
    
    def _calculate_semantic_score(self, ai_analysis: Dict[str, Any]) -> float:
        """Calculate semantic similarity score from AI analysis"""
        try:
            # Get semantic similarity from AI analysis
            semantic_similarity = ai_analysis.get('semantic_similarity', 0.0)
            
            # Convert to 0-100 scale
            semantic_score = semantic_similarity * 100
            
            # Adjust score based on other AI analysis factors
            matching_skills = len(ai_analysis.get('matching_skills', []))
            missing_skills = len(ai_analysis.get('missing_skills', []))
            
            # Apply adjustments
            if matching_skills > 0:
                semantic_score += min(10, matching_skills * 2)  # Bonus for matching skills
            
            if missing_skills > 0:
                semantic_score -= min(15, missing_skills * 3)  # Penalty for missing skills
            
            return max(0, min(100, semantic_score))
            
        except Exception as e:
            return 0.0
    
    def _calculate_skill_match_score(self, resume: Resume, job_description: JobDescription) -> float:
        """Calculate skill matching score"""
        try:
            # Get all required skills
            must_have_skills = job_description.must_have_skills or []
            nice_to_have_skills = job_description.nice_to_have_skills or []
            
            if not must_have_skills and not nice_to_have_skills:
                return 85.0  # Default score if no skills specified
            
            resume_lower = resume.content.lower()
            
            # Calculate must-have skills match
            must_have_matches = 0
            for skill in must_have_skills:
                if self._skill_present_in_text(skill, resume_lower):
                    must_have_matches += 1
            
            # Calculate nice-to-have skills match
            nice_to_have_matches = 0
            for skill in nice_to_have_skills:
                if self._skill_present_in_text(skill, resume_lower):
                    nice_to_have_matches += 1
            
            # Calculate weighted score
            must_have_score = (must_have_matches / len(must_have_skills)) * 0.8 if must_have_skills else 0.8
            nice_to_have_score = (nice_to_have_matches / len(nice_to_have_skills)) * 0.2 if nice_to_have_skills else 0.2
            
            total_score = (must_have_score + nice_to_have_score) * 100
            
            return min(100, total_score)
            
        except Exception as e:
            return 0.0
    
    def _skill_present_in_text(self, skill: str, text: str) -> bool:
        """Check if a skill is present in text using fuzzy matching"""
        skill_lower = skill.lower().strip()
        
        # Direct match
        if skill_lower in text:
            return True
        
        # Fuzzy match for variations
        skill_words = skill_lower.split()
        text_words = text.split()
        
        # Check if all skill words are present
        matches = sum(1 for word in skill_words if word in text_words)
        return matches == len(skill_words)
    
    def _calculate_experience_score(self, resume: Resume, job_description: JobDescription) -> float:
        """Calculate experience level matching score"""
        try:
            resume_text = resume.content.lower()
            required_level = job_description.experience_level or ""
            
            # Extract years of experience from resume
            years_experience = self._extract_years_of_experience(resume_text)
            
            # Map experience levels to years
            level_mapping = {
                'entry level': (0, 2),
                'mid level': (2, 5),
                'senior level': (5, 10),
                'executive': (10, float('inf'))
            }
            
            required_level_lower = required_level.lower()
            if required_level_lower not in level_mapping:
                return 75.0  # Default score if level not specified
            
            min_years, max_years = level_mapping[required_level_lower]
            
            # Calculate score based on experience match
            if min_years <= years_experience <= max_years:
                return 100.0  # Perfect match
            elif years_experience < min_years:
                # Underqualified
                gap = min_years - years_experience
                return max(30, 100 - (gap * 15))  # Penalty for each year under
            else:
                # Overqualified (less penalty than underqualified)
                excess = years_experience - max_years
                return max(70, 100 - (excess * 5))  # Smaller penalty for overqualification
            
        except Exception as e:
            return 75.0  # Default score on error
    
    def _extract_years_of_experience(self, text: str) -> int:
        """Extract years of experience from resume text"""
        try:
            # Look for explicit mentions of years of experience
            patterns = [
                r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
                r'(\d+)\+?\s*years?\s*in\s*\w+',
                r'experience[:\s]*(\d+)\+?\s*years?',
                r'(\d+)\+?\s*years?\s*professional'
            ]
            
            years_found = []
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                years_found.extend([int(match) for match in matches])
            
            if years_found:
                # Return the maximum years found (most likely total experience)
                return max(years_found)
            
            # If no explicit years mentioned, estimate from work history
            # Count job positions or education graduation years
            job_indicators = len(re.findall(r'\b(?:worked|employed|position|role)\b', text, re.IGNORECASE))
            
            if job_indicators >= 3:
                return 5  # Estimated senior level
            elif job_indicators >= 2:
                return 3  # Estimated mid level
            elif job_indicators >= 1:
                return 1  # Estimated entry level
            else:
                return 0  # Fresh graduate
                
        except Exception as e:
            return 1  # Default to 1 year on error
    
    def _determine_verdict(self, score: float) -> str:
        """Determine hiring verdict based on overall score"""
        if score >= 75:
            return "High"
        elif score >= 50:
            return "Medium"
        else:
            return "Low"
    
    def calculate_detailed_metrics(self, resume: Resume, job_description: JobDescription, 
                                 ai_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate additional detailed metrics for analysis"""
        try:
            metrics = {}
            
            # Resume quality metrics
            metrics['resume_length'] = len(resume.content.split())
            metrics['sections_identified'] = self._count_resume_sections(resume.content)
            
            # Job description analysis
            metrics['jd_complexity'] = self._assess_jd_complexity(job_description)
            
            # Match quality metrics
            metrics['exact_skill_matches'] = len(ai_analysis.get('matching_skills', []))
            metrics['missing_critical_skills'] = len(ai_analysis.get('missing_skills', []))
            
            # Confidence score
            metrics['confidence_score'] = self._calculate_confidence_score(
                resume, job_description, ai_analysis
            )
            
            return metrics
            
        except Exception as e:
            return {}
    
    def _count_resume_sections(self, resume_text: str) -> int:
        """Count identifiable sections in resume"""
        sections = [
            'experience', 'education', 'skills', 'projects', 'certifications',
            'achievements', 'summary', 'objective', 'contact'
        ]
        
        text_lower = resume_text.lower()
        found_sections = sum(1 for section in sections if section in text_lower)
        
        return found_sections
    
    def _assess_jd_complexity(self, job_description: JobDescription) -> str:
        """Assess job description complexity"""
        skill_count = len((job_description.must_have_skills or []) + 
                         (job_description.nice_to_have_skills or []))
        
        if skill_count > 10:
            return "High"
        elif skill_count > 5:
            return "Medium"
        else:
            return "Low"
    
    def _calculate_confidence_score(self, resume: Resume, job_description: JobDescription, 
                                  ai_analysis: Dict[str, Any]) -> float:
        """Calculate confidence score for the analysis"""
        try:
            confidence_factors = []
            
            # Resume quality factor
            resume_length = len(resume.content.split())
            if 200 <= resume_length <= 800:
                confidence_factors.append(0.9)
            else:
                confidence_factors.append(0.6)
            
            # Job description completeness
            if job_description.must_have_skills and job_description.description:
                confidence_factors.append(0.9)
            else:
                confidence_factors.append(0.7)
            
            # AI analysis quality
            if ai_analysis.get('reasoning') and len(ai_analysis.get('matching_skills', [])) > 0:
                confidence_factors.append(0.95)
            else:
                confidence_factors.append(0.8)
            
            # Calculate average confidence
            avg_confidence = sum(confidence_factors) / len(confidence_factors)
            
            return round(avg_confidence * 100, 1)
            
        except Exception as e:
            return 75.0  # Default confidence score
