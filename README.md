Deploying the Eval backend to Hugging Face Spaces (Docker)

Prerequisites
- A Hugging Face account and a new Space (set type to Docker)
- Your OpenAI API key (if using OpenAI evaluation)

Files included
- app.py: Flask API exposing endpoints under /api
- models.py, utils.py, evaluator.py, chunking_utils.py, config.py
- requirements.txt: minimal dependencies for CPU deployment
- Dockerfile: builds and runs the Flask API on port 7860

Environment variables
- OPENAI_API_KEY: set in the Space Secrets if Config.EVALUATION_MODEL is 'openai'
- FLASK_SECRET_KEY (optional)
- DATABASE_URL (optional; defaults to sqlite:///evalai_new.db)

Build and run (locally)
```bash
docker build -t eval-backend ./Eval
docker run -p 7860:7860 -e OPENAI_API_KEY=YOUR_KEY eval-backend
```

Deploy on Spaces
1) Create a new Space, select Docker as the SDK
2) Upload the contents of the Eval/ folder to the Space root
3) In the Space Settings, add a Secret named OPENAI_API_KEY
4) Spaces will build using the Dockerfile and expose the API at / on port 7860

API quick check
```bash
curl -s https://<your-space>.hf.space/ | jq
```
