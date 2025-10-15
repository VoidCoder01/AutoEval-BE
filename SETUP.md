# AutoEval Setup Guide

## Quick Start (3 steps)

### 1. Install Dependencies

```bash
cd AutoEval
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the AutoEval directory:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=sk-your-api-key-here
FLASK_SECRET_KEY=your-random-secret-key
DATABASE_URL=sqlite:///autoeval.db
EVALUATION_MODEL=openai
```

**Getting an OpenAI API Key:**
1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Create a new API key
4. Copy and paste it into your `.env` file

### 3. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## Using AutoEval

### For Hackathon Hosts:

1. Go to **Host Dashboard** (`/host`)
2. Fill in the hackathon details:
   - Name and description
   - Evaluation prompt (guide for AI scoring)
   - Deadline (optional)
3. Click **Create Hackathon**
4. Share the submission link with participants
5. View submissions and leaderboard anytime

### For Participants:

1. Go to **Submit Project** (`/participant`)
2. Select the hackathon
3. Enter team details
4. Upload your files:
   - Source code (.py, .js, .java, etc.)
   - README.md or documentation
   - Or upload a .zip file with everything
5. Submit and get instant AI evaluation!

### Viewing Results:

- **Individual Results**: Automatically redirected after submission
- **Leaderboard**: Available from the home page or host dashboard
- **Detailed Feedback**: Click on any submission to see AI-generated insights

## Testing the Platform

### Quick Test Workflow:

1. **Create a test hackathon:**
   - Name: "Test Hackathon"
   - Description: "Build a simple Python calculator"
   - Evaluation Prompt: "Evaluate based on code quality, functionality, and documentation"

2. **Submit a test project:**
   - Create a simple `calculator.py` file
   - Write a basic README.md
   - Submit through the participant interface

3. **View results:**
   - Check the evaluation scores
   - Review AI-generated feedback
   - View the leaderboard

## Troubleshooting

### Database Issues
If you encounter database errors:
```bash
# Delete the old database
rm autoeval.db
# Restart the app (it will create a new database)
python app.py
```

### OpenAI API Errors
- Ensure your API key is valid
- Check you have credits in your OpenAI account
- Verify the key is correctly set in `.env`

### File Upload Issues
- Maximum file size: 16MB
- Allowed formats: .py, .js, .java, .cpp, .c, .txt, .md, .pdf, .zip, .html, .css, .json
- For large projects, use .zip archives

### Port Already in Use
If port 5000 is busy:
```bash
# Edit app.py and change the port
app.run(debug=True, host='0.0.0.0', port=8080)
```

## Production Deployment

For production use:

1. Set a strong `FLASK_SECRET_KEY`
2. Use PostgreSQL instead of SQLite
3. Disable debug mode
4. Use a production WSGI server (gunicorn)
5. Set up HTTPS

Example production command:
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## Features

✅ AI-powered evaluation using GPT-4
✅ Multiple criteria scoring (Relevance, Complexity, Creativity, Documentation)
✅ Real-time leaderboards
✅ Detailed AI feedback
✅ File upload support (including .zip archives)
✅ Beautiful, responsive UI
✅ Instant results

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the README.md
3. Check OpenAI API status
4. Verify your environment variables

## Architecture

- **Backend**: Flask (Python)
- **Database**: SQLite (default) or PostgreSQL
- **AI**: OpenAI GPT-4 API
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **File Storage**: Local filesystem

