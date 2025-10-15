# 🚀 AutoEval - Quick Start Guide

## Step-by-Step Setup (5 minutes)

### Step 1: Navigate to the Project
```bash
cd E:\Anushka\blackpearl1\hackathon\AutoEval
```

### Step 2: Create Environment File

Create a file named `.env` in the AutoEval folder with this content:

```
OPENAI_API_KEY=sk-your-openai-api-key-here
FLASK_SECRET_KEY=my-super-secret-key-12345
DATABASE_URL=sqlite:///autoeval.db
EVALUATION_MODEL=openai
```

**Important**: Replace `sk-your-openai-api-key-here` with your actual OpenAI API key.

Don't have an API key? Get one here: https://platform.openai.com/api-keys

### Step 3: Install Dependencies

Using your existing virtual environment:
```bash
cd ..
venv\Scripts\activate
cd AutoEval
pip install -r requirements.txt
```

### Step 4: Run the Application

**Option A - Simple Start:**
```bash
python app.py
```

**Option B - Using the startup script (Windows):**
```bash
start.bat
```

**Option C - Using the startup script (Linux/Mac):**
```bash
chmod +x start.sh
./start.sh
```

### Step 5: Open in Browser

Once you see "Running on http://127.0.0.1:5000", open your browser and go to:
```
http://localhost:5000
```

## 🎯 First Test

1. Go to **Host Dashboard** (http://localhost:5000/host)
2. Create a test hackathon
3. Go to **Submit Project** (http://localhost:5000/participant)
4. Upload the test files (`test_sample.py` and `test_README.md`)
5. See instant AI evaluation!

## ⚠️ Troubleshooting

### "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### "OpenAI API Error"
- Check your API key in `.env`
- Ensure you have credits in your OpenAI account
- Verify the key starts with `sk-`

### "Port 5000 already in use"
Edit `app.py` and change the port:
```python
app.run(debug=True, host='0.0.0.0', port=8080)
```
Then visit `http://localhost:8080`

### Database errors
```bash
# Delete the database file and restart
del autoeval.db
python app.py
```

## 📱 What You'll See

- **Home Page**: Overview and active hackathons
- **Host Dashboard**: Create and manage hackathons
- **Submit Project**: Upload code for evaluation
- **Results**: AI scores and detailed feedback
- **Leaderboard**: Rankings for all submissions

## 🎉 You're Ready!

The platform is now running. Create hackathons, submit projects, and see AI-powered evaluation in action!

