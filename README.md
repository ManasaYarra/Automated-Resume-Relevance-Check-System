# AI-Powered Resume Matching System

An intelligent resume-job description matching system that uses AI and machine learning to analyze candidate resumes against job requirements, providing comprehensive scoring and feedback for placement teams.

## Features

- **Smart Document Processing**: Extract text from PDF and DOCX files
- **AI-Powered Analysis**: Uses OpenAI GPT models for semantic analysis and intelligent insights
- **Hybrid Scoring System**: Combines keyword matching, semantic similarity, and skill analysis
- **Interactive Dashboard**: User-friendly Streamlit interface for placement teams
- **Comprehensive Reporting**: Detailed analysis with missing skills, suggestions, and improvement recommendations
- **PostgreSQL Database**: Robust data storage with search and filtering capabilities

## Tech Stack

- **Backend**: Python 3.11
- **Frontend**: Streamlit
- **Database**: PostgreSQL
- **AI/ML**: OpenAI GPT, scikit-learn, TF-IDF, fuzzy matching
- **Document Processing**: PyMuPDF, python-docx, docx2txt

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd resume-matcher
```

2. Install Python 3.11 (if not already installed)

3. Install dependencies:
```bash
pip install -r requirements.txt
# OR if using the project file:
pip install -e .
```

4. Set up environment variables:
```bash
# Database Configuration (PostgreSQL)
export PGHOST=your_db_host
export PGPORT=5432
export PGDATABASE=your_db_name
export PGUSER=your_db_user
export PGPASSWORD=your_db_password

# OpenAI API Key
export OPENAI_API_KEY=your_openai_api_key
```

## Usage

1. Start the application:
```bash
streamlit run app.py --server.port 5000
```

2. Open your browser and navigate to `http://localhost:5000`

3. Use the application:
   - **Job Description Upload**: Upload and configure job descriptions
   - **Resume Analysis**: Upload resumes and analyze against job descriptions
   - **Dashboard**: View analytics and performance metrics
   - **Search Results**: Search and filter analysis results

## Application Flow

1. **Upload Job Description**: Placement teams upload job descriptions with requirements and skills
2. **Upload Resume**: Students or HR upload candidate resumes for analysis
3. **AI Analysis**: System processes documents using:
   - Text extraction and cleaning
   - Keyword matching with fuzzy logic
   - Semantic similarity using OpenAI embeddings
   - Comprehensive AI analysis for insights
4. **Scoring**: Hybrid scoring algorithm combining multiple factors
5. **Results**: Detailed report with scores, missing elements, and suggestions

## File Structure

```
├── app.py                 # Main Streamlit application
├── database.py           # Database connection and operations
├── document_parser.py    # PDF/DOCX text extraction
├── ai_analyzer.py        # OpenAI integration and AI analysis
├── scoring_engine.py     # Hybrid scoring algorithms
├── models.py            # Data models and classes
├── utils.py             # Utility functions
├── pyproject.toml       # Project dependencies
├── .streamlit/
│   └── config.toml      # Streamlit configuration
└── README.md           # This file
```

## Configuration

### Streamlit Configuration (`.streamlit/config.toml`):
```toml
[server]
headless = true
address = "0.0.0.0"
port = 5000
```

### Database Schema

The application automatically creates the following tables:
- `job_descriptions`: Store job postings and requirements
- `resumes`: Store candidate resume data
- `analysis_results`: Store matching analysis results

## API Keys Required

1. **OpenAI API Key**: Required for AI analysis features
   - Get from: https://platform.openai.com/api-keys
   - Used for: Semantic analysis, embeddings, intelligent insights

2. **PostgreSQL Database**: Required for data persistence
   - Can use local PostgreSQL or cloud services like Neon, Supabase

## Features in Detail

### Document Processing
- Supports PDF, DOCX, and TXT files
- Intelligent text extraction with cleanup
- Handles various document formats and layouts

### AI Analysis
- **Semantic Similarity**: Using OpenAI embeddings
- **Missing Skills Detection**: AI identifies gaps
- **Improvement Suggestions**: Actionable recommendations
- **Experience Assessment**: Evaluates candidate experience level

### Scoring Algorithm
- **Keyword Score (40%)**: TF-IDF and fuzzy matching
- **Semantic Score (35%)**: AI-powered similarity
- **Skill Match (15%)**: Specific skill alignment
- **Experience Match (10%)**: Experience level fit

### Dashboard Features
- Real-time analytics and metrics
- Search and filtering capabilities
- Exportable results
- Performance tracking

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions or issues:
1. Check the documentation above
2. Review the code comments for implementation details
3. Create an issue in the GitHub repository

## Deployment

For production deployment:
1. Use a production-grade PostgreSQL database
2. Set up proper environment variable management
3. Configure SSL/TLS for security
4. Consider using Docker for containerization
5. Set up monitoring and logging