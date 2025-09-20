import os
import re
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import mimetypes

def validate_file_type(filename: str, allowed_extensions: List[str]) -> bool:
    """Validate if file type is allowed"""
    if not filename:
        return False
    
    file_extension = filename.lower().split('.')[-1]
    return file_extension in [ext.lower() for ext in allowed_extensions]

def get_file_size_mb(file_content: bytes) -> float:
    """Get file size in MB"""
    return len(file_content) / (1024 * 1024)

def validate_email(email: str) -> bool:
    """Validate email format"""
    if not email:
        return False
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email.strip()) is not None

def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    if not phone:
        return True  # Phone is optional
    
    # Remove all non-digit characters for validation
    digits_only = re.sub(r'[^\d]', '', phone)
    
    # Check if it has 10-15 digits (international format)
    return 10 <= len(digits_only) <= 15

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep punctuation
    text = re.sub(r'[^\w\s\.,;:!?()-]', '', text)
    
    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    return text.strip()

def extract_skills_from_text(text: str) -> List[str]:
    """Extract potential skills from text using keyword matching"""
    # Common skill keywords database
    skill_keywords = {
        'programming_languages': [
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby',
            'php', 'swift', 'kotlin', 'go', 'rust', 'scala', 'r', 'matlab',
            'perl', 'shell', 'bash', 'powershell'
        ],
        'web_technologies': [
            'html', 'css', 'react', 'angular', 'vue', 'node.js', 'express',
            'django', 'flask', 'spring', 'bootstrap', 'jquery', 'webpack',
            'sass', 'less', 'rest api', 'graphql', 'json', 'xml'
        ],
        'databases': [
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
            'oracle', 'sqlite', 'cassandra', 'dynamodb', 'firebase'
        ],
        'cloud_platforms': [
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins',
            'terraform', 'ansible', 'gitlab', 'github actions'
        ],
        'data_science': [
            'machine learning', 'deep learning', 'artificial intelligence',
            'data analysis', 'statistics', 'pandas', 'numpy', 'scikit-learn',
            'tensorflow', 'pytorch', 'tableau', 'power bi', 'spark'
        ],
        'soft_skills': [
            'leadership', 'communication', 'teamwork', 'problem solving',
            'project management', 'agile', 'scrum', 'time management'
        ]
    }
    
    text_lower = text.lower()
    found_skills = []
    
    for category, skills in skill_keywords.items():
        for skill in skills:
            if skill in text_lower:
                found_skills.append(skill.title())
    
    return list(set(found_skills))  # Remove duplicates

def format_score(score: float, decimal_places: int = 1) -> str:
    """Format score for display"""
    return f"{score:.{decimal_places}f}%"

def get_verdict_color(verdict: str) -> str:
    """Get color code for verdict display"""
    color_map = {
        'High': '#28a745',    # Green
        'Medium': '#ffc107',  # Yellow/Orange
        'Low': '#dc3545'      # Red
    }
    return color_map.get(verdict, '#6c757d')  # Default gray

def calculate_processing_time(start_time: datetime, end_time: datetime) -> float:
    """Calculate processing time in seconds"""
    return (end_time - start_time).total_seconds()

def generate_file_hash(file_content: bytes) -> str:
    """Generate MD5 hash for file content"""
    return hashlib.md5(file_content).hexdigest()

def is_valid_file_size(file_content: bytes, max_size_mb: float = 10.0) -> bool:
    """Check if file size is within limits"""
    size_mb = get_file_size_mb(file_content)
    return size_mb <= max_size_mb

def extract_years_from_text(text: str) -> List[int]:
    """Extract years from text"""
    year_pattern = r'\b(19|20)\d{2}\b'
    years = re.findall(year_pattern, text)
    return [int(year) for year in years if year]

def estimate_reading_time(text: str, words_per_minute: int = 200) -> int:
    """Estimate reading time in minutes"""
    word_count = len(text.split())
    return max(1, word_count // words_per_minute)

def create_summary_stats(scores: List[float]) -> Dict[str, float]:
    """Create summary statistics for a list of scores"""
    if not scores:
        return {
            'count': 0,
            'average': 0.0,
            'min': 0.0,
            'max': 0.0,
            'median': 0.0
        }
    
    scores_sorted = sorted(scores)
    count = len(scores)
    
    return {
        'count': count,
        'average': sum(scores) / count,
        'min': min(scores),
        'max': max(scores),
        'median': scores_sorted[count // 2] if count % 2 == 1 else 
                 (scores_sorted[count // 2 - 1] + scores_sorted[count // 2]) / 2
    }

def format_date(date: datetime, format_string: str = "%Y-%m-%d %H:%M") -> str:
    """Format datetime for display"""
    if not date:
        return "N/A"
    return date.strftime(format_string)

def get_time_ago(date: datetime) -> str:
    """Get human-readable time difference"""
    if not date:
        return "Unknown"
    
    now = datetime.now()
    if date.tzinfo:
        # Handle timezone-aware datetimes
        from datetime import timezone
        now = now.replace(tzinfo=timezone.utc)
    
    diff = now - date
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "Just now"

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    if not filename:
        return "unnamed_file"
    
    # Remove path components
    filename = os.path.basename(filename)
    
    # Replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Limit length
    name, ext = os.path.splitext(filename)
    if len(name) > 50:
        name = name[:50]
    
    return f"{name}{ext}"

def validate_job_description_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate job description data"""
    errors = []
    
    # Required fields
    if not data.get('title'):
        errors.append("Job title is required")
    
    if not data.get('description'):
        errors.append("Job description content is required")
    
    # Validate experience level
    valid_levels = ['Entry Level', 'Mid Level', 'Senior Level', 'Executive']
    if data.get('experience_level') and data['experience_level'] not in valid_levels:
        errors.append(f"Experience level must be one of: {', '.join(valid_levels)}")
    
    # Validate employment type
    valid_types = ['Full-time', 'Part-time', 'Contract', 'Internship']
    if data.get('employment_type') and data['employment_type'] not in valid_types:
        errors.append(f"Employment type must be one of: {', '.join(valid_types)}")
    
    return len(errors) == 0, errors

def validate_resume_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate resume data"""
    errors = []
    
    # Required fields
    if not data.get('candidate_name'):
        errors.append("Candidate name is required")
    
    if not data.get('candidate_email'):
        errors.append("Candidate email is required")
    elif not validate_email(data['candidate_email']):
        errors.append("Invalid email format")
    
    if not data.get('content'):
        errors.append("Resume content is required")
    
    # Validate phone if provided
    if data.get('candidate_phone') and not validate_phone(data['candidate_phone']):
        errors.append("Invalid phone number format")
    
    return len(errors) == 0, errors

def extract_contact_info_from_text(text: str) -> Dict[str, Optional[str]]:
    """Extract contact information from text"""
    contact_info: Dict[str, Optional[str]] = {
        'email': None,
        'phone': None,
        'linkedin': None,
        'github': None
    }
    
    # Email extraction
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    if email_match:
        contact_info['email'] = email_match.group()
    
    # Phone extraction
    phone_patterns = [
        r'\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
        r'\b\d{10}\b',
        r'\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b'
    ]
    
    for pattern in phone_patterns:
        phone_match = re.search(pattern, text)
        if phone_match:
            contact_info['phone'] = phone_match.group()
            break
    
    # LinkedIn extraction
    linkedin_match = re.search(r'linkedin\.com/in/([a-zA-Z0-9\-]+)', text, re.IGNORECASE)
    if linkedin_match:
        contact_info['linkedin'] = f"linkedin.com/in/{linkedin_match.group(1)}"
    
    # GitHub extraction
    github_match = re.search(r'github\.com/([a-zA-Z0-9\-]+)', text, re.IGNORECASE)
    if github_match:
        contact_info['github'] = f"github.com/{github_match.group(1)}"
    
    return contact_info

def create_error_response(message: str, details: Optional[str] = None) -> Dict[str, Any]:
    """Create standardized error response"""
    response = {
        'success': False,
        'error': message,
        'timestamp': datetime.now().isoformat()
    }
    
    if details:
        response['details'] = details
    
    return response

def create_success_response(data: Any, message: str = "Operation successful") -> Dict[str, Any]:
    """Create standardized success response"""
    return {
        'success': True,
        'message': message,
        'data': data,
        'timestamp': datetime.now().isoformat()
    }

def log_analysis_event(event_type: str, details: Dict[str, Any]) -> None:
    """Log analysis events for monitoring"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'event_type': event_type,
        'details': details
    }
    
    # In a production environment, this would log to a proper logging system
    print(f"[{log_entry['timestamp']}] {event_type}: {details}")

def get_mime_type(filename: str) -> str:
    """Get MIME type for file"""
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or 'application/octet-stream'

def is_text_file(filename: str) -> bool:
    """Check if file is a text file"""
    text_extensions = ['.txt', '.md', '.csv', '.json', '.xml']
    return any(filename.lower().endswith(ext) for ext in text_extensions)

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def normalize_skill_name(skill: str) -> str:
    """Normalize skill name for consistent matching"""
    if not skill:
        return ""
    
    # Convert to lowercase and strip whitespace
    normalized = skill.lower().strip()
    
    # Common normalizations
    skill_mappings = {
        'js': 'javascript',
        'ts': 'typescript',
        'py': 'python',
        'node': 'node.js',
        'react.js': 'react',
        'vue.js': 'vue',
        'angular.js': 'angular',
        'postgres': 'postgresql',
        'mongo': 'mongodb'
    }
    
    return skill_mappings.get(normalized, normalized)

def parse_skill_list(skills_text: str) -> List[str]:
    """Parse comma-separated skills text into list"""
    if not skills_text:
        return []
    
    # Split by comma and clean each skill
    skills = [skill.strip() for skill in skills_text.split(',')]
    
    # Remove empty skills and normalize
    skills = [normalize_skill_name(skill) for skill in skills if skill.strip()]
    
    # Remove duplicates while preserving order
    seen = set()
    unique_skills = []
    for skill in skills:
        if skill not in seen:
            seen.add(skill)
            unique_skills.append(skill)
    
    return unique_skills
