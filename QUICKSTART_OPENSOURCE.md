# 🚀 AutoEval - Quick Start (Open-Source Models)

## No API Keys Required! 🎉

This version uses **UniXCoder** and **CodeLlama** - completely free and open-source AI models.

## Step-by-Step Setup (10 minutes)

### Step 1: Navigate to Project
```bash
cd E:\Anushka\blackpearl1\hackathon
```

### Step 2: Activate Virtual Environment
```bash
venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r AutoEval\requirements.txt
```

**Note**: First time will download AI models (~2-4GB). This takes 5-10 minutes depending on internet speed.

### Step 4: Create .env File (Optional)

Create `AutoEval\.env` with:
```
FLASK_SECRET_KEY=my-secret-key-12345
DATABASE_URL=sqlite:///autoeval.db
```

### Step 5: Run the Application
```bash
cd AutoEval
python app.py
```

**First Run**: Models will download automatically. Wait for "Models loaded successfully!"

### Step 6: Open Browser
```
http://localhost:5000
```

## What Makes This Special?

✅ **No API Keys** - Completely free, no OpenAI account needed
✅ **Privacy** - All processing happens locally on your machine  
✅ **Offline** - Works without internet (after initial model download)
✅ **UniXCoder** - Microsoft's state-of-the-art code understanding model
✅ **CodeLlama** - Meta's powerful code generation model

## System Requirements

- **RAM**: 8GB minimum (16GB recommended for CodeLlama)
- **Storage**: 5GB free space for models
- **GPU**: Optional (CUDA). Will use CPU if no GPU available
- **Internet**: Only needed for first-time model download

## Performance

- **With GPU**: ~5-10 seconds per evaluation
- **With CPU**: ~30-60 seconds per evaluation  
- **First evaluation**: Slower due to model loading

## Troubleshooting

### "Out of Memory" Error
```python
# In config.py, set:
USE_CODELLAMA = False  # Disable CodeLlama to save RAM
```

### Models Download Slowly
- Models are large (2-4GB total)
- Download happens automatically on first run
- Be patient, it only happens once

### CPU Too Slow
- Consider using GPU if available
- Or disable CodeLlama for faster evaluation
- UniXCoder alone still provides excellent results

## Test It!

1. Go to http://localhost:5000/host
2. Create a hackathon
3. Go to /participant
4. Upload `test_sample.py` and `test_README.md`
5. Watch AI evaluation happen locally!

## Models Used

- **UniXCoder** (`microsoft/unixcoder-base`): 
  - Code embeddings and similarity scoring
  - Works for all programming languages
  
- **CodeLlama** (`codellama/CodeLlama-7b-Instruct-hf`):
  - Detailed code explanations
  - Optional (can disable to save RAM)

## Next Steps

Read `DEMO.md` for presentation tips!

