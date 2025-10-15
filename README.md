# AutoEval – AI-Powered Hackathon Scoring Platform

AutoEval is an AI-driven platform designed to automatically evaluate hackathon projects based on a prompt provided by the host. Participants submit their projects (code + documentation), and the system scores them across multiple criteria.

## Features

- **Host Dashboard**: Create hackathons with custom evaluation criteria
- **Participant Submission**: Upload code and documentation for evaluation
- **AI-Powered Scoring**: Automatic evaluation using UniXCoder embeddings and OpenAI
- **Multi-Criteria Analysis**: Scores across relevance, technical complexity, creativity, and documentation quality
- **Detailed Feedback**: AI-generated explanations for scores

## Quick Start

1. **Install Dependencies**:
```bash
cd AutoEval
pip install -r requirements.txt
```

2. **Set Up Environment**:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

3. **Run the Application**:
```bash
python app.py
```

4. **Access the Platform**:
- Open http://localhost:5000 in your browser
- Host Interface: Create and manage hackathons
- Participant Interface: Submit projects and view scores

## Evaluation Criteria

The platform evaluates projects across:
- **Relevance** (0-10): How well the project matches the hackathon theme
- **Technical Complexity** (0-10): Code quality and technical sophistication
- **Creativity** (0-10): Innovation and unique approaches
- **Documentation** (0-10): Quality and completeness of documentation

## Tech Stack

- **Backend**: Flask (Python)
- **AI Models**: UniXCoder, OpenAI GPT-4
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: SQLite

## API Endpoints

- `POST /api/hackathon` - Create a new hackathon
- `GET /api/hackathons` - List all hackathons
- `POST /api/submit` - Submit a project
- `GET /api/hackathon/<id>/submissions` - View submissions
- `POST /api/evaluate/<submission_id>` - Trigger evaluation
- `GET /api/results/<submission_id>` - Get evaluation results

