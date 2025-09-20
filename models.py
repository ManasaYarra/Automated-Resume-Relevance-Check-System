from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class JobDescription:
    """Model for job description data"""
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    experience_level: Optional[str] = None
    department: Optional[str] = None
    employment_type: Optional[str] = None
    description: str = ""
    must_have_skills: List[str] = field(default_factory=list)
    nice_to_have_skills: List[str] = field(default_factory=list)
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Post-initialization processing"""
        # Ensure skills are lists
        if isinstance(self.must_have_skills, str):
            self.must_have_skills = [skill.strip() for skill in self.must_have_skills.split(',') if skill.strip()]
        if isinstance(self.nice_to_have_skills, str):
            self.nice_to_have_skills = [skill.strip() for skill in self.nice_to_have_skills.split(',') if skill.strip()]
    
    def get_all_skills(self) -> List[str]:
        """Get all skills (must-have + nice-to-have)"""
        return self.must_have_skills + self.nice_to_have_skills
    
    def get_skill_count(self) -> int:
        """Get total number of skills required"""
        return len(self.get_all_skills())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'experience_level': self.experience_level,
            'department': self.department,
            'employment_type': self.employment_type,
            'description': self.description,
            'must_have_skills': self.must_have_skills,
            'nice_to_have_skills': self.nice_to_have_skills,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

@dataclass
class Resume:
    """Model for resume data"""
    candidate_name: str
    candidate_email: str
    content: str
    candidate_phone: Optional[str] = None
    candidate_location: Optional[str] = None
    filename: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Post-initialization processing"""
        # Clean and validate email
        if self.candidate_email:
            self.candidate_email = self.candidate_email.strip().lower()
        
        # Clean content
        if self.content:
            self.content = self.content.strip()
    
    def get_word_count(self) -> int:
        """Get word count of resume content"""
        return len(self.content.split()) if self.content else 0
    
    def get_character_count(self) -> int:
        """Get character count of resume content"""
        return len(self.content) if self.content else 0
    
    def has_contact_info(self) -> bool:
        """Check if resume has basic contact information"""
        return bool(self.candidate_name and self.candidate_email)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'candidate_name': self.candidate_name,
            'candidate_email': self.candidate_email,
            'candidate_phone': self.candidate_phone,
            'candidate_location': self.candidate_location,
            'content': self.content,
            'filename': self.filename,
            'created_at': self.created_at
        }

@dataclass
class AnalysisResult:
    """Model for analysis result data"""
    resume: Resume
    job_description: JobDescription
    relevance_score: int
    verdict: str
    keyword_score: Optional[int] = None
    semantic_score: Optional[int] = None
    missing_skills: List[str] = field(default_factory=list)
    missing_qualifications: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    ai_reasoning: str = ""
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    
    # Additional analysis fields
    matching_skills: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    experience_assessment: str = ""
    education_assessment: str = ""
    
    def __post_init__(self):
        """Post-initialization processing"""
        # Ensure score is within valid range
        self.relevance_score = max(0, min(100, self.relevance_score))
        
        # Validate verdict
        valid_verdicts = ['High', 'Medium', 'Low']
        if self.verdict not in valid_verdicts:
            if self.relevance_score >= 75:
                self.verdict = 'High'
            elif self.relevance_score >= 50:
                self.verdict = 'Medium'
            else:
                self.verdict = 'Low'
    
    def get_score_category(self) -> str:
        """Get score category description"""
        if self.relevance_score >= 85:
            return "Excellent Match"
        elif self.relevance_score >= 75:
            return "Good Match"
        elif self.relevance_score >= 60:
            return "Fair Match"
        elif self.relevance_score >= 40:
            return "Poor Match"
        else:
            return "Very Poor Match"
    
    def get_recommendation(self) -> str:
        """Get hiring recommendation based on score and analysis"""
        if self.verdict == 'High':
            return "Strongly recommend for interview"
        elif self.verdict == 'Medium':
            return "Consider for interview with reservations"
        else:
            return "Not recommended for this position"
    
    def has_critical_missing_skills(self) -> bool:
        """Check if candidate has critical missing skills"""
        return len(self.missing_skills) > 3
    
    def get_improvement_priority(self) -> List[str]:
        """Get prioritized list of improvement areas"""
        priority_areas = []
        
        # Add missing skills as high priority
        if self.missing_skills:
            priority_areas.extend(self.missing_skills[:3])  # Top 3 missing skills
        
        # Add missing qualifications
        if self.missing_qualifications:
            priority_areas.extend(self.missing_qualifications[:2])  # Top 2 qualifications
        
        return priority_areas
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'relevance_score': self.relevance_score,
            'keyword_score': self.keyword_score,
            'semantic_score': self.semantic_score,
            'verdict': self.verdict,
            'missing_skills': self.missing_skills,
            'missing_qualifications': self.missing_qualifications,
            'matching_skills': self.matching_skills,
            'suggestions': self.suggestions,
            'ai_reasoning': self.ai_reasoning,
            'strengths': self.strengths,
            'weaknesses': self.weaknesses,
            'experience_assessment': self.experience_assessment,
            'education_assessment': self.education_assessment,
            'created_at': self.created_at,
            'resume': self.resume.to_dict() if self.resume else None,
            'job_description': self.job_description.to_dict() if self.job_description else None
        }

@dataclass
class MatchingCriteria:
    """Model for defining matching criteria and weights"""
    keyword_weight: float = 0.4
    semantic_weight: float = 0.35
    skill_weight: float = 0.15
    experience_weight: float = 0.1
    minimum_score_threshold: int = 40
    high_score_threshold: int = 75
    medium_score_threshold: int = 50
    
    def __post_init__(self):
        """Post-initialization validation"""
        # Ensure weights sum to 1.0
        total_weight = (self.keyword_weight + self.semantic_weight + 
                       self.skill_weight + self.experience_weight)
        
        if abs(total_weight - 1.0) > 0.01:  # Allow small floating point errors
            raise ValueError("Weights must sum to 1.0")
        
        # Validate thresholds
        if not (0 <= self.minimum_score_threshold <= 100):
            raise ValueError("Minimum score threshold must be between 0 and 100")
        
        if not (self.minimum_score_threshold <= self.medium_score_threshold <= 
                self.high_score_threshold <= 100):
            raise ValueError("Score thresholds must be in ascending order")
    
    def get_verdict_for_score(self, score: int) -> str:
        """Get verdict based on score and thresholds"""
        if score >= self.high_score_threshold:
            return "High"
        elif score >= self.medium_score_threshold:
            return "Medium"
        else:
            return "Low"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'keyword_weight': self.keyword_weight,
            'semantic_weight': self.semantic_weight,
            'skill_weight': self.skill_weight,
            'experience_weight': self.experience_weight,
            'minimum_score_threshold': self.minimum_score_threshold,
            'high_score_threshold': self.high_score_threshold,
            'medium_score_threshold': self.medium_score_threshold
        }

@dataclass
class SystemMetrics:
    """Model for system performance metrics"""
    total_resumes_processed: int = 0
    total_job_descriptions: int = 0
    average_processing_time: float = 0.0
    high_score_matches: int = 0
    medium_score_matches: int = 0
    low_score_matches: int = 0
    average_relevance_score: float = 0.0
    last_updated: Optional[datetime] = None
    
    def get_total_matches(self) -> int:
        """Get total number of matches processed"""
        return self.high_score_matches + self.medium_score_matches + self.low_score_matches
    
    def get_success_rate(self) -> float:
        """Get percentage of high + medium matches"""
        total = self.get_total_matches()
        if total == 0:
            return 0.0
        
        successful_matches = self.high_score_matches + self.medium_score_matches
        return (successful_matches / total) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'total_resumes_processed': self.total_resumes_processed,
            'total_job_descriptions': self.total_job_descriptions,
            'average_processing_time': self.average_processing_time,
            'high_score_matches': self.high_score_matches,
            'medium_score_matches': self.medium_score_matches,
            'low_score_matches': self.low_score_matches,
            'average_relevance_score': self.average_relevance_score,
            'total_matches': self.get_total_matches(),
            'success_rate': self.get_success_rate(),
            'last_updated': self.last_updated
        }
