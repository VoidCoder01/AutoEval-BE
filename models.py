from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import json

db = SQLAlchemy()

class Hackathon(db.Model):
    __tablename__ = 'hackathons'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    evaluation_prompt = db.Column(db.Text, nullable=False)
    criteria = db.Column(db.Text, nullable=False)  # JSON string of criteria
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    deadline = db.Column(db.DateTime)
    host_email = db.Column(db.String(200))
    
    submissions = db.relationship('Submission', backref='hackathon', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'evaluation_prompt': self.evaluation_prompt,
            'criteria': json.loads(self.criteria) if self.criteria else [],
            'created_at': self.created_at.isoformat(),
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'host_email': self.host_email,
            'submission_count': len(self.submissions)
        }


class Submission(db.Model):
    __tablename__ = 'submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    hackathon_id = db.Column(db.Integer, db.ForeignKey('hackathons.id'), nullable=False)
    team_name = db.Column(db.String(200), nullable=False)
    participant_email = db.Column(db.String(200), nullable=False)
    project_name = db.Column(db.String(200), nullable=False)
    project_description = db.Column(db.Text)
    code_content = db.Column(db.Text)  # Extracted code content
    documentation_content = db.Column(db.Text)  # Extracted documentation
    file_paths = db.Column(db.Text)  # JSON string of uploaded file paths
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    evaluated = db.Column(db.Boolean, default=False)
    
    evaluation = db.relationship('Evaluation', backref='submission', uselist=False, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'hackathon_id': self.hackathon_id,
            'team_name': self.team_name,
            'participant_email': self.participant_email,
            'project_name': self.project_name,
            'project_description': self.project_description,
            'submitted_at': self.submitted_at.isoformat(),
            'evaluated': self.evaluated,
            'file_count': len(json.loads(self.file_paths)) if self.file_paths else 0
        }


class Evaluation(db.Model):
    __tablename__ = 'evaluations'
    
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submissions.id'), nullable=False)
    relevance_score = db.Column(db.Float, default=0.0)
    technical_complexity_score = db.Column(db.Float, default=0.0)
    creativity_score = db.Column(db.Float, default=0.0)
    documentation_score = db.Column(db.Float, default=0.0)
    productivity_score = db.Column(db.Float, default=0.0)  # NEW: 5th evaluation metric
    overall_score = db.Column(db.Float, default=0.0)
    feedback = db.Column(db.Text)  # AI-generated feedback
    detailed_scores = db.Column(db.Text)  # JSON string of detailed criteria scores
    evaluated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'submission_id': self.submission_id,
            'relevance_score': self.relevance_score,
            'technical_complexity_score': self.technical_complexity_score,
            'creativity_score': self.creativity_score,
            'documentation_score': self.documentation_score,
            'productivity_score': self.productivity_score,
            'overall_score': self.overall_score,
            'feedback': self.feedback,
            'detailed_scores': json.loads(self.detailed_scores) if self.detailed_scores else {},
                    # Ensure UTC marker so clients can convert correctly
                    'evaluated_at': (
                        (self.evaluated_at.replace(tzinfo=timezone.utc) if self.evaluated_at.tzinfo is None else self.evaluated_at.astimezone(timezone.utc))
                        .isoformat()
                        .replace('+00:00', 'Z')
                    )
        }


