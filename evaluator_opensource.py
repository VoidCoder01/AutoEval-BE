"""
AI Evaluator using Open-Source Models
- UniXCoder for code embeddings and scoring
- CodeLlama for detailed explanations (optional)
"""

import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import torch
from transformers import AutoTokenizer, AutoModel, pipeline
from config import Config


class OpenSourceEvaluator:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
        # Load UniXCoder for code understanding
        print("Loading UniXCoder model...")
        self.unixcoder_tokenizer = AutoTokenizer.from_pretrained("microsoft/unixcoder-base")
        self.unixcoder_model = AutoModel.from_pretrained("microsoft/unixcoder-base").to(self.device)
        
        # Load CodeLlama for explanations (if enabled)
        self.codellama_pipeline = None
        if Config.USE_CODELLAMA:
            try:
                print("Loading CodeLlama for explanations...")
                # Using a smaller variant that can run on CPU
                self.codellama_pipeline = pipeline(
                    "text-generation",
                    model="codellama/CodeLlama-7b-Instruct-hf",
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    device_map="auto" if self.device == "cuda" else None,
                    max_length=512
                )
            except Exception as e:
                print(f"CodeLlama not available: {e}")
                print("Falling back to rule-based explanations")
        
        print("Models loaded successfully!")
    
    def evaluate_submission(self, submission, hackathon):
        """
        Evaluate a submission using UniXCoder and CodeLlama
        """
        print(f"Evaluating submission: {submission.project_name}")
        
        # Get embeddings for code and documentation
        code_embedding = self._get_code_embedding(submission.code_content or "")
        doc_embedding = self._get_code_embedding(submission.documentation_content or "")
        theme_embedding = self._get_code_embedding(hackathon.description + " " + hackathon.evaluation_prompt)
        
        # Calculate scores
        relevance_score = self._calculate_relevance(code_embedding, doc_embedding, theme_embedding)
        technical_score = self._calculate_technical_complexity(submission.code_content or "")
        creativity_score = self._calculate_creativity(submission.code_content or "", submission.documentation_content or "")
        documentation_score = self._calculate_documentation_quality(submission.documentation_content or "")
        
        overall_score = (relevance_score + technical_score + creativity_score + documentation_score) / 4
        
        # Generate feedback
        feedback = self._generate_feedback(
            submission,
            hackathon,
            relevance_score,
            technical_score,
            creativity_score,
            documentation_score
        )
        
        detailed_scores = {
            "relevance_justification": f"Score {relevance_score:.1f}/10 - Alignment with theme and requirements",
            "technical_justification": f"Score {technical_score:.1f}/10 - Code complexity and implementation quality",
            "creativity_justification": f"Score {creativity_score:.1f}/10 - Innovation and unique approach",
            "documentation_justification": f"Score {documentation_score:.1f}/10 - Documentation clarity and completeness"
        }
        
        return {
            'relevance_score': round(relevance_score, 2),
            'technical_complexity_score': round(technical_score, 2),
            'creativity_score': round(creativity_score, 2),
            'documentation_score': round(documentation_score, 2),
            'overall_score': round(overall_score, 2),
            'feedback': feedback,
            'detailed_scores': json.dumps(detailed_scores)
        }
    
    def _get_code_embedding(self, text):
        """Get embeddings using UniXCoder"""
        if not text or len(text.strip()) == 0:
            return np.zeros(768)  # UniXCoder base dimension
        
        # Truncate if too long
        text = text[:2000]
        
        tokens = self.unixcoder_tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        tokens = {k: v.to(self.device) for k, v in tokens.items()}
        
        with torch.no_grad():
            outputs = self.unixcoder_model(**tokens)
            embedding = outputs.last_hidden_state.mean(dim=1).cpu().numpy()[0]
        
        return embedding
    
    def _calculate_relevance(self, code_emb, doc_emb, theme_emb):
        """Calculate how relevant the project is to the theme"""
        # Combine code and doc embeddings
        project_emb = (code_emb + doc_emb) / 2
        
        # Calculate cosine similarity with theme
        similarity = cosine_similarity([project_emb], [theme_emb])[0][0]
        
        # Convert similarity (-1 to 1) to score (0 to 10)
        score = ((similarity + 1) / 2) * 10
        
        # Ensure minimum score of 3 if there's any content
        if np.any(code_emb) or np.any(doc_emb):
            score = max(score, 3.0)
        
        return min(10.0, max(0.0, score))
    
    def _calculate_technical_complexity(self, code):
        """Analyze technical complexity of the code"""
        if not code or len(code.strip()) == 0:
            return 2.0
        
        score = 5.0  # Base score
        
        # Count various code patterns
        lines = code.split('\n')
        non_empty_lines = [l for l in lines if l.strip()]
        
        # More lines generally means more complexity
        if len(non_empty_lines) > 100:
            score += 1.0
        if len(non_empty_lines) > 300:
            score += 1.0
        
        # Check for classes and functions
        class_count = code.count('class ')
        function_count = code.count('def ') + code.count('function ')
        
        if class_count > 2:
            score += 0.5
        if function_count > 5:
            score += 0.5
        if function_count > 10:
            score += 0.5
        
        # Check for advanced patterns
        advanced_patterns = [
            'async ', 'await ', 'generator', 'decorator',
            'try:', 'except:', 'finally:',
            'import ', 'from ',
            'lambda ', 'yield ',
        ]
        
        for pattern in advanced_patterns:
            if pattern in code:
                score += 0.2
        
        # Check for comments and documentation
        comment_count = code.count('#') + code.count('//') + code.count('"""')
        if comment_count > 10:
            score += 0.5
        
        return min(10.0, max(0.0, score))
    
    def _calculate_creativity(self, code, documentation):
        """Assess creativity and innovation"""
        score = 5.0  # Base score
        
        combined_text = (code + " " + documentation).lower()
        
        # Look for innovative keywords
        innovation_keywords = [
            'ai', 'machine learning', 'neural', 'algorithm',
            'optimization', 'novel', 'innovative', 'unique',
            'creative', 'original', 'advanced', 'intelligent',
            'automation', 'api', 'integration', 'real-time'
        ]
        
        for keyword in innovation_keywords:
            if keyword in combined_text:
                score += 0.3
        
        # Check for multiple file types (indicates comprehensive solution)
        file_extensions = ['.py', '.js', '.html', '.css', '.json', '.yml']
        for ext in file_extensions:
            if ext in combined_text:
                score += 0.2
        
        # Bonus for good project structure indicators
        structure_indicators = ['readme', 'documentation', 'test', 'config', 'requirements']
        for indicator in structure_indicators:
            if indicator in combined_text:
                score += 0.2
        
        return min(10.0, max(0.0, score))
    
    def _calculate_documentation_quality(self, documentation):
        """Evaluate documentation quality"""
        if not documentation or len(documentation.strip()) < 50:
            return 2.0
        
        score = 5.0  # Base score
        
        doc_lower = documentation.lower()
        
        # Check for key sections
        important_sections = [
            'overview', 'introduction', 'description',
            'installation', 'setup', 'usage', 'how to',
            'features', 'requirements', 'dependencies',
            'example', 'api', 'configuration'
        ]
        
        for section in important_sections:
            if section in doc_lower:
                score += 0.3
        
        # Check documentation length
        words = documentation.split()
        if len(words) > 100:
            score += 0.5
        if len(words) > 300:
            score += 0.5
        if len(words) > 500:
            score += 0.5
        
        # Check for code examples in documentation
        if '```' in documentation or '    ' in documentation:
            score += 0.5
        
        # Check for proper markdown formatting
        markdown_elements = ['#', '##', '###', '-', '*', '1.', '2.']
        for element in markdown_elements:
            if element in documentation:
                score += 0.1
        
        return min(10.0, max(0.0, score))
    
    def _generate_feedback(self, submission, hackathon, rel_score, tech_score, crea_score, doc_score):
        """Generate detailed feedback"""
        
        feedback_parts = []
        
        # Overall assessment
        overall = (rel_score + tech_score + crea_score + doc_score) / 4
        if overall >= 8:
            feedback_parts.append(f"Excellent work on '{submission.project_name}'! This submission demonstrates strong technical skills and good alignment with the hackathon theme.")
        elif overall >= 6:
            feedback_parts.append(f"Good submission for '{submission.project_name}'. The project shows solid understanding and implementation.")
        else:
            feedback_parts.append(f"Thank you for your submission of '{submission.project_name}'. There are areas for improvement to strengthen the project.")
        
        # Relevance feedback
        if rel_score >= 7:
            feedback_parts.append(f"The project aligns well with the theme '{hackathon.name}' and addresses the requirements effectively.")
        else:
            feedback_parts.append(f"Consider strengthening the connection to the hackathon theme '{hackathon.name}' to improve relevance.")
        
        # Technical feedback
        if tech_score >= 7:
            feedback_parts.append("The technical implementation shows good complexity and code quality.")
        elif tech_score >= 5:
            feedback_parts.append("The technical implementation is functional but could benefit from more advanced features or better code organization.")
        else:
            feedback_parts.append("The technical implementation needs more depth. Consider adding more features, better error handling, or improved code structure.")
        
        # Creativity feedback
        if crea_score >= 7:
            feedback_parts.append("The approach demonstrates creativity and innovation.")
        else:
            feedback_parts.append("The solution could be more innovative. Think about unique features or novel approaches to the problem.")
        
        # Documentation feedback
        if doc_score >= 7:
            feedback_parts.append("The documentation is clear and comprehensive, making it easy to understand the project.")
        elif doc_score >= 5:
            feedback_parts.append("The documentation is adequate but could be more detailed with setup instructions, usage examples, and feature descriptions.")
        else:
            feedback_parts.append("The documentation needs significant improvement. Include a README with project overview, setup instructions, and usage examples.")
        
        # Use CodeLlama for additional insights if available
        if self.codellama_pipeline and len(submission.code_content or "") > 50:
            try:
                code_snippet = (submission.code_content or "")[:500]
                prompt = f"Briefly explain what this code does:\n{code_snippet}"
                llama_output = self.codellama_pipeline(prompt, max_new_tokens=100)[0]['generated_text']
                feedback_parts.append(f"\nCode Analysis: {llama_output}")
            except:
                pass  # Skip if CodeLlama fails
        
        return " ".join(feedback_parts)

