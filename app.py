from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from models import db, Hackathon, Submission, Evaluation
from evaluator_opensource import OpenSourceEvaluator
from utils import allowed_file, save_uploaded_file, extract_code_from_files, extract_documentation
from config import Config
import json
from datetime import datetime
import os

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Initialize database
db.init_app(app)

# Initialize AI evaluator (will load models on first use)
evaluator = None

def get_evaluator():
    global evaluator
    if evaluator is None:
        print("Initializing AI models...")
        evaluator = OpenSourceEvaluator()
    return evaluator

# Create tables
with app.app_context():
    db.create_all()
    print("Database initialized!")

# Routes
@app.route('/')
def index():
    """Main host interface - upload projects and evaluate"""
    return render_template('index.html')

# API Endpoints
@app.route('/api/hackathons', methods=['GET'])
def get_hackathons():
    """Get all hackathons"""
    hackathons = Hackathon.query.order_by(Hackathon.created_at.desc()).all()
    return jsonify([h.to_dict() for h in hackathons])

@app.route('/api/hackathon', methods=['POST'])
def create_hackathon():
    """Create a new hackathon"""
    try:
        data = request.json
        
        # Default criteria if not provided
        default_criteria = [
            {'name': 'Relevance', 'weight': 0.25, 'description': 'Alignment with theme'},
            {'name': 'Technical Complexity', 'weight': 0.25, 'description': 'Code quality and sophistication'},
            {'name': 'Creativity', 'weight': 0.25, 'description': 'Innovation and uniqueness'},
            {'name': 'Documentation', 'weight': 0.25, 'description': 'Quality and completeness'}
        ]
        
        hackathon = Hackathon(
            name=data['name'],
            description=data['description'],
            evaluation_prompt=data.get('evaluation_prompt', 'Evaluate this hackathon project.'),
            criteria=json.dumps(data.get('criteria', default_criteria)),
            host_email=data.get('host_email', ''),
            deadline=datetime.fromisoformat(data['deadline']) if data.get('deadline') else None
        )
        
        db.session.add(hackathon)
        db.session.commit()
        
        return jsonify(hackathon.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/hackathon/<int:hackathon_id>', methods=['GET'])
def get_hackathon(hackathon_id):
    """Get a specific hackathon"""
    hackathon = Hackathon.query.get_or_404(hackathon_id)
    return jsonify(hackathon.to_dict())

@app.route('/api/batch-upload', methods=['POST'])
def batch_upload():
    """Upload and evaluate multiple projects at once"""
    try:
        # Get evaluation prompt
        evaluation_prompt = request.form.get('evaluation_prompt')
        evaluation_name = request.form.get('evaluation_name', 'Project Evaluation')
        
        if not evaluation_prompt:
            return jsonify({'error': 'Evaluation prompt is required'}), 400
        
        # Create evaluation batch
        hackathon = Hackathon(
            name=evaluation_name,
            description=evaluation_prompt,
            evaluation_prompt=evaluation_prompt,
            criteria=json.dumps([
                {'name': 'Relevance', 'weight': 0.25},
                {'name': 'Creativity', 'weight': 0.25},
                {'name': 'Technical Complexity', 'weight': 0.25},
                {'name': 'Documentation', 'weight': 0.25}
            ])
        )
        db.session.add(hackathon)
        db.session.flush()
        
        # Get number of projects
        num_projects = int(request.form.get('num_projects', 0))
        results = []
        
        for i in range(num_projects):
            project_name = request.form.get(f'project_name_{i}', f'Project {i+1}')
            project_desc = request.form.get(f'project_desc_{i}', '')
            files = request.files.getlist(f'project_files_{i}')
            
            if not files:
                continue
            
            # Create submission
            submission = Submission(
                hackathon_id=hackathon.id,
                team_name=project_name,
                participant_email='host@evaluation.com',
                project_name=project_name,
                project_description=project_desc
            )
            db.session.add(submission)
            db.session.flush()
            
            # Save files
            file_paths = []
            for file in files:
                if file and allowed_file(file.filename):
                    file_path = save_uploaded_file(file, submission.id)
                    file_paths.append(file_path)
            
            # Extract content
            submission.file_paths = json.dumps(file_paths)
            submission.code_content = extract_code_from_files(file_paths)
            submission.documentation_content = extract_documentation(file_paths, project_desc)
            
            # Evaluate
            eval_engine = get_evaluator()
            scores = eval_engine.evaluate_submission(submission, hackathon)
            
            evaluation = Evaluation(
                submission_id=submission.id,
                relevance_score=scores['relevance_score'],
                technical_complexity_score=scores['technical_complexity_score'],
                creativity_score=scores['creativity_score'],
                documentation_score=scores['documentation_score'],
                overall_score=scores['overall_score'],
                feedback=scores['feedback'],
                detailed_scores=scores['detailed_scores']
            )
            submission.evaluated = True
            db.session.add(evaluation)
            
            results.append({
                'project_name': project_name,
                'overall_score': scores['overall_score']
            })
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'evaluation_id': hackathon.id,
            'total_projects': len(results)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400

@app.route('/api/evaluate/<int:submission_id>', methods=['POST'])
def evaluate_submission_endpoint(submission_id):
    """Trigger evaluation for a submission"""
    try:
        result = evaluate_submission_internal(submission_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

def evaluate_submission_internal(submission_id):
    """Internal function to evaluate a submission"""
    submission = Submission.query.get(submission_id)
    if not submission:
        raise ValueError('Submission not found')
    
    hackathon = Hackathon.query.get(submission.hackathon_id)
    if not hackathon:
        raise ValueError('Hackathon not found')
    
    # Check if already evaluated
    if submission.evaluation:
        db.session.delete(submission.evaluation)
        db.session.commit()
    
    # Perform AI evaluation using open-source models
    eval_engine = get_evaluator()
    scores = eval_engine.evaluate_submission(submission, hackathon)
    
    # Create evaluation record
    evaluation = Evaluation(
        submission_id=submission.id,
        relevance_score=scores['relevance_score'],
        technical_complexity_score=scores['technical_complexity_score'],
        creativity_score=scores['creativity_score'],
        documentation_score=scores['documentation_score'],
        overall_score=scores['overall_score'],
        feedback=scores['feedback'],
        detailed_scores=scores['detailed_scores']
    )
    
    submission.evaluated = True
    
    db.session.add(evaluation)
    db.session.commit()
    
    return evaluation.to_dict()

@app.route('/api/hackathon/<int:hackathon_id>/submissions', methods=['GET'])
def get_submissions(hackathon_id):
    """Get all submissions for a hackathon"""
    hackathon = Hackathon.query.get_or_404(hackathon_id)
    submissions = Submission.query.filter_by(hackathon_id=hackathon_id).order_by(Submission.submitted_at.desc()).all()
    
    result = []
    for sub in submissions:
        sub_dict = sub.to_dict()
        if sub.evaluation:
            sub_dict['evaluation'] = sub.evaluation.to_dict()
        result.append(sub_dict)
    
    return jsonify(result)

@app.route('/api/results/<int:submission_id>', methods=['GET'])
def get_results(submission_id):
    """Get evaluation results for a submission"""
    submission = Submission.query.get_or_404(submission_id)
    
    result = submission.to_dict()
    if submission.evaluation:
        result['evaluation'] = submission.evaluation.to_dict()
        result['hackathon'] = submission.hackathon.to_dict()
    else:
        return jsonify({'error': 'Submission not yet evaluated'}), 404
    
    return jsonify(result)

@app.route('/api/leaderboard/<int:hackathon_id>', methods=['GET'])
def get_leaderboard(hackathon_id):
    """Get leaderboard for a hackathon"""
    hackathon = Hackathon.query.get_or_404(hackathon_id)
    
    submissions = Submission.query.filter_by(
        hackathon_id=hackathon_id,
        evaluated=True
    ).join(Evaluation).order_by(Evaluation.overall_score.desc()).all()
    
    leaderboard = []
    for idx, sub in enumerate(submissions):
        leaderboard.append({
            'rank': idx + 1,
            'team_name': sub.team_name,
            'project_name': sub.project_name,
            'overall_score': sub.evaluation.overall_score,
            'submission_id': sub.id
        })
    
    return jsonify({
        'hackathon': hackathon.to_dict(),
        'leaderboard': leaderboard
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

