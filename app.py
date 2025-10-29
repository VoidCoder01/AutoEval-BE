from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, Hackathon, Submission, Evaluation
from utils import allowed_file, save_uploaded_file, extract_code_from_files, extract_documentation
from config import Config
import json
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH  # Explicitly set the upload limit
CORS(app)

# Initialize database
db.init_app(app)

# Initialize AI evaluator (will load models on first use)
evaluator = None

def get_evaluator():
    global evaluator
    if evaluator is None:
        print(f"Initializing AI evaluator (mode: {Config.EVALUATION_MODEL})...")
        
        if Config.EVALUATION_MODEL == 'openai':
            from evaluator import AIEvaluator
            evaluator = AIEvaluator()
            print("✅ Using OpenAI GPT-4o for evaluation")
        else:
            from evaluator_opensource import OpenSourceEvaluator
            evaluator = OpenSourceEvaluator()
            print("✅ Using Open-Source LLM for evaluation")
    
    return evaluator

# Create tables
with app.app_context():
    db.create_all()
    print("Database initialized with productivity_score column!")

# Routes
@app.route('/')
def index():
    """API server info - Frontend is served separately on port 5173"""
    return jsonify({
        'name': 'EvalAI API',
        'version': '1.0',
        'status': 'running',
        'frontend_url': 'http://localhost:5173',
        'message': 'API is running. Access the UI at http://localhost:5173'
    })

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
            {'name': 'Relevance', 'weight': 0.20, 'description': 'Alignment with theme'},
            {'name': 'Technical Complexity', 'weight': 0.20, 'description': 'Code quality and sophistication'},
            {'name': 'Creativity', 'weight': 0.20, 'description': 'Innovation and uniqueness'},
            {'name': 'Documentation', 'weight': 0.20, 'description': 'Quality and completeness'},
            {'name': 'Productivity', 'weight': 0.20, 'description': 'Code organization and efficiency'}
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


@app.route('/api/submissions', methods=['POST'])
def create_submission():
    """Create a single submission and evaluate it"""
    try:
        # Get form data
        hackathon_id = request.form.get('hackathon_id')
        team_name = request.form.get('team_name', 'Team')
        participant_email = request.form.get('participant_email', 'participant@autoeval.ai')
        project_name = request.form.get('project_name')
        project_description = request.form.get('project_description', '')
        
        if not hackathon_id or not project_name:
            return jsonify({'error': 'Hackathon ID and project name are required'}), 400
        
        # Get hackathon
        hackathon = Hackathon.query.get(int(hackathon_id))
        if not hackathon:
            return jsonify({'error': 'Hackathon not found'}), 404
        
        # Get uploaded files
        files = request.files.getlist('project_files')
        if not files:
            return jsonify({'error': 'At least one file is required'}), 400
        
        # Create submission
        submission = Submission(
            hackathon_id=hackathon.id,
            team_name=team_name,
            participant_email=participant_email,
            project_name=project_name,
            project_description=project_description
        )
        db.session.add(submission)
        db.session.flush()
        
        # Save files
        file_paths = []
        for file in files:
            if file and allowed_file(file.filename):
                file_path = save_uploaded_file(file, submission.id)
                file_paths.append(file_path)
        
        if not file_paths:
            db.session.rollback()
            return jsonify({'error': 'No valid files uploaded'}), 400
        
        # Extract content
        submission.file_paths = json.dumps(file_paths)
        submission.code_content = extract_code_from_files(file_paths)
        submission.documentation_content = extract_documentation(file_paths, project_description)
        
        # Evaluate
        print(f"🎯 Starting AI evaluation for project: {project_name}")
        print(f"📁 Files uploaded: {len(file_paths)}")
        print(f"📝 Code content length: {len(submission.code_content)} characters")
        print(f"📄 Documentation length: {len(submission.documentation_content)} characters")
        
        eval_engine = get_evaluator()
        scores = eval_engine.evaluate_submission(submission, hackathon)
        
        print("🎉 AI evaluation completed!")
        print(f"⭐ Overall score: {scores['overall_score']}/10")
        
        # Create evaluation
        evaluation = Evaluation(
            submission_id=submission.id,
            relevance_score=scores['relevance_score'],
            technical_complexity_score=scores['technical_complexity_score'],
            creativity_score=scores['creativity_score'],
            documentation_score=scores['documentation_score'],
            productivity_score=scores['productivity_score'],
            overall_score=scores['overall_score'],
            feedback=scores['feedback'],
            detailed_scores=scores['detailed_scores']
        )
        
        submission.evaluated = True
        db.session.add(evaluation)
        db.session.commit()
        
        response_data = {
            'success': True,
            'id': submission.id,
            'hackathon_id': hackathon.id,
            'overall_score': scores['overall_score']
        }
        
        print("📤 Sending response to frontend:")
        print(f"   ✅ Success: {response_data['success']}")
        print(f"   🆔 Submission ID: {response_data['id']}")
        print(f"   🏆 Hackathon ID: {response_data['hackathon_id']}")
        print(f"   ⭐ Overall Score: {response_data['overall_score']}")
        print("=" * 50)
        
        return jsonify(response_data), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating submission: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/hackathon/<int:hackathon_id>/submissions', methods=['GET'])
def get_hackathon_submissions(hackathon_id):
    """Get all submissions for a hackathon"""
    try:
        hackathon = Hackathon.query.get_or_404(hackathon_id)
        submissions = Submission.query.filter_by(hackathon_id=hackathon_id).order_by(Submission.submitted_at.desc()).all()
        
        result = []
        for submission in submissions:
            sub_dict = submission.to_dict()
            if submission.evaluation:
                sub_dict['evaluation'] = submission.evaluation.to_dict()
            result.append(sub_dict)
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error getting hackathon submissions: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug/submissions', methods=['GET'])
def debug_submissions():
    """Debug endpoint to list all submissions"""
    try:
        submissions = Submission.query.all()
        result = []
        for sub in submissions:
            result.append({
                'id': sub.id,
                'project_name': sub.project_name,
                'team_name': sub.team_name,
                'evaluated': sub.evaluated,
                'has_evaluation': sub.evaluation is not None,
                'submitted_at': sub.submitted_at.isoformat() if sub.submitted_at else None
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/results/<int:submission_id>', methods=['GET'])
def get_individual_result(submission_id):
    """Get evaluation results for a specific submission"""
    try:
        print(f"🔍 Looking for submission ID: {submission_id}")
        submission = Submission.query.get(submission_id)
        
        if not submission:
            print(f"❌ Submission {submission_id} not found")
            return jsonify({'error': f'Submission {submission_id} not found'}), 404
        
        print(f"✅ Found submission: {submission.project_name}")
        
        if not submission.evaluation:
            print(f"⚠️ Submission {submission_id} not yet evaluated")
            return jsonify({'error': 'Submission not yet evaluated'}), 404
        
        print(f"✅ Evaluation found for submission {submission_id}")
        
        result = submission.to_dict()
        result['evaluation'] = submission.evaluation.to_dict()
        result['hackathon'] = submission.hackathon.to_dict()
        
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Error getting individual result: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)


