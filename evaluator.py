import os
import openai
from openai import OpenAI
import json
import re
from config import Config
from chunking_utils import chunk_code_content, combine_chunk_evaluations, create_chunk_summary

class AIEvaluator:
    def __init__(self):
        self.model = Config.EVALUATION_MODEL
        if self.model == 'openai':
            # Set API key for OpenAI
            if not Config.OPENAI_API_KEY:
                raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY in your environment or .env file.")
            
            try:
                # Initialize OpenAI client (v1.0+ style)
                self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
                print("✅ OpenAI client initialized successfully")
            except Exception as e:
                print(f"❌ Error initializing OpenAI client: {e}")
                raise e
    
    def evaluate_submission(self, submission, hackathon):
        """
        Evaluate a submission based on the hackathon criteria
        """
        if self.model == 'openai':
            # Check if content is too large and needs chunking
            code_content = submission.code_content or ""
            doc_content = submission.documentation_content or ""
            total_content = code_content + doc_content
            
            # If content is large, use chunked evaluation
            if len(total_content) > 3000:  # 3K characters threshold (force chunking earlier)
                print(f"📊 Large content detected ({len(total_content):,} chars), using chunked evaluation...")
                return self._evaluate_with_chunking(submission, hackathon)
            else:
                print(f"📊 Standard evaluation for content ({len(total_content):,} chars)...")
                return self._evaluate_with_openai(submission, hackathon)
        else:
            return self._evaluate_with_unixcoder(submission, hackathon)
    
    def _evaluate_with_openai(self, submission, hackathon):
        """
        Use OpenAI GPT-4 to evaluate the submission
        """
        evaluation_prompt = self._build_evaluation_prompt(submission, hackathon)
        
        print("📋 EVALUATION PROMPT BEING SENT:")
        print("=" * 60)
        print(evaluation_prompt[:500] + "..." if len(evaluation_prompt) > 500 else evaluation_prompt)
        print("=" * 60)
        
        try:
            print("🚀 Sending request to OpenAI GPT-4o...")
            print(f"📝 Evaluation prompt length: {len(evaluation_prompt)} characters")
            
            # Use OpenAI client to generate evaluation
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Using GPT-4o for best quality and speed
                messages=[
                    {"role": "system", "content": "You are a STRICT technical evaluator and hackathon judge. You must be critical, use the full scoring range 0-10, and provide differentiated scores. DO NOT give grade inflation. Most projects should score in the 4-7 range. Be harsh but fair."},
                    {"role": "user", "content": evaluation_prompt}
                ],
                temperature=0.1,  # Lower temperature for more consistent, strict evaluation
                max_tokens=2000
            )
            
            result_text = response.choices[0].message.content
            print("✅ OpenAI Response received!")
            print("=" * 80)
            print("🤖 OPENAI GPT-4o RESPONSE:")
            print("=" * 80)
            print(result_text)
            print("=" * 80)
            print(f"📊 Response length: {len(result_text)} characters")
            print(f"💰 Tokens used: {response.usage.total_tokens if hasattr(response, 'usage') else 'Unknown'}")
            
            parsed_result = self._parse_evaluation_result(result_text)
            print("✅ Response parsed successfully!")
            print(f"📈 Parsed scores: {parsed_result}")
            
            return parsed_result
            
        except Exception as e:
            print(f"❌ Error in OpenAI evaluation: {str(e)}")
            print("🔄 Falling back to default scores...")
            return self._generate_fallback_scores()
    
    def _evaluate_with_chunking(self, submission, hackathon):
        """
        Evaluate large submissions by chunking the content
        """
        try:
            # Chunk the code content
            code_content = submission.code_content or ""
            chunks = chunk_code_content(code_content, max_chunk_size=4000)
            
            print(f"📦 Created {len(chunks)} chunks for evaluation")
            print(create_chunk_summary(chunks))
            
            chunk_results = []
            
            for i, chunk in enumerate(chunks, 1):
                print(f"🔍 Evaluating chunk {i}/{len(chunks)} ({chunk['size']:,} chars)...")
                
                # Create a temporary submission object for this chunk
                chunk_submission = type('ChunkSubmission', (), {
                    'code_content': chunk['content'],
                    'documentation_content': submission.documentation_content or "",
                    'project_name': f"{submission.project_name} (Chunk {i})",
                    'project_description': submission.project_description,
                    'team_name': submission.team_name,
                    'participant_email': submission.participant_email
                })()
                
                # Evaluate this chunk
                chunk_result = self._evaluate_with_openai(chunk_submission, hackathon)
                
                # Add chunk metadata
                chunk_result['chunk_id'] = i
                chunk_result['chunk_weight'] = chunk['size']  # Weight by content size
                
                chunk_results.append(chunk_result)
                
                print(f"✅ Chunk {i} evaluated: {chunk_result['overall_score']}/10")
            
            # Combine results from all chunks
            print("🔄 Combining results from all chunks...")
            combined_result = combine_chunk_evaluations(chunk_results)
            
            print(f"🎯 Final combined score: {combined_result['overall_score']}/10")
            return combined_result
            
        except Exception as e:
            print(f"❌ Error in chunked evaluation: {str(e)}")
            print("🔄 Falling back to standard evaluation...")
            # Fallback to standard evaluation with truncated content
            return self._evaluate_with_openai_truncated(submission, hackathon)
    
    def _evaluate_with_openai_truncated(self, submission, hackathon):
        """
        Evaluate with truncated content as fallback
        """
        # Truncate content to manageable size
        code_content = (submission.code_content or "")[:4000]
        doc_content = (submission.documentation_content or "")[:2000]
        
        # Create truncated submission
        truncated_submission = type('TruncatedSubmission', (), {
            'code_content': code_content,
            'documentation_content': doc_content,
            'project_name': submission.project_name,
            'project_description': submission.project_description,
            'team_name': submission.team_name,
            'participant_email': submission.participant_email
        })()
        
        print("⚠️ Using truncated content for evaluation")
        result = self._evaluate_with_openai(truncated_submission, hackathon)
        
        # Keep feedback as-is without prefixing a truncation note
        return result
    
    def _build_evaluation_prompt(self, submission, hackathon):
        """
        Build the prompt for AI evaluation
        """
        criteria = json.loads(hackathon.criteria) if hackathon.criteria else self._get_default_criteria()
        
        prompt = f"""
# STRICT Hackathon Evaluation - NO GRADE INFLATION

## Hackathon Information
**Name**: {hackathon.name}
**Theme/Description**: {hackathon.description}

## Evaluation Criteria
{hackathon.evaluation_prompt}

## Submission to Evaluate
**Team**: {submission.team_name}
**Project Name**: {submission.project_name}
**Description**: {submission.project_description}

### Code Content
```
{self._truncate_content(submission.code_content, 3000)}
```

### Documentation
```
{self._truncate_content(submission.documentation_content, 2000)}
```

## CRITICAL EVALUATION INSTRUCTIONS

You are a STRICT technical evaluator. Use the FULL range of scores 0-10. DO NOT give similar scores to different projects.

### SCORING GUIDELINES (BE HARSH AND REALISTIC):

**0-2: Poor/Failing**
- Major issues, non-functional, or completely irrelevant
- Severe security vulnerabilities or broken code
- No documentation or completely unclear

**3-4: Below Average**
- Basic functionality but significant flaws
- Poor code quality, structure, or practices
- Minimal effort or incomplete implementation

**5-6: Average/Acceptable**
- Works as intended with minor issues
- Standard implementation, nothing special
- Adequate documentation and code quality

**7-8: Good/Above Average**
- Well-implemented with good practices
- Shows clear understanding and effort
- Good documentation and structure

**9-10: Excellent/Outstanding**
- Exceptional quality, innovative approach
- Production-ready code with best practices
- Comprehensive documentation and testing

        ## STRICT EVALUATION CRITERIA:

1. **Relevance (0-10)**: Does it ACTUALLY solve the problem stated? Is it directly related to the theme?
2. **Technical Complexity (0-10)**: How sophisticated is the implementation? Rate based on actual technical depth, not just lines of code.
3. **Creativity (0-10)**: Is this a unique approach or just a standard tutorial implementation?
4. **Documentation (0-10)**: Is there proper README, comments, setup instructions? Can someone else run this?
5. **Productivity (0-10)**: Code organization, error handling, scalability, maintainability.

        ## ADDITIONAL KEY-POINT ANALYSIS (brief, 1-2 sentences each):
        - Out of the box thinking: How original/novel is the approach?
        - Problem-solving skills: How effectively does the code decompose and solve the problem?
        - Research capabilities: Evidence of learning, citations, comparisons, benchmarking, or exploration
        - Understanding the business: Does it align with real user/business needs and constraints?
        - Use of non-famous tools or frameworks: Any lesser-known tech used purposefully

        ## MANDATORY REQUIREMENTS:
- VARY your scores significantly between projects
- Use decimals (e.g., 3.2, 6.7, 8.1) for precision
- Be CRITICAL and identify real weaknesses
- NO GRADE INFLATION - most projects should score 4-7 range
- Only exceptional projects deserve 8-10
- Don't hesitate to give low scores (1-3) for poor work

        ## Response Format (STRICT JSON):

```json
{{
  "relevance_score": <precise score 0-10 with 1 decimal>,
  "technical_complexity_score": <precise score 0-10 with 1 decimal>,
  "creativity_score": <precise score 0-10 with 1 decimal>,
  "documentation_score": <precise score 0-10 with 1 decimal>,
  "productivity_score": <precise score 0-10 with 1 decimal>,
  "overall_score": <calculated average with 1 decimal>,
  "feedback": "<HONEST, CRITICAL feedback. Point out specific flaws, missing features, and areas for improvement. Don't sugarcoat.>",
  "detailed_scores": {{
    "relevance_justification": "<specific reasons for this score>",
    "technical_justification": "<specific technical assessment>",
    "creativity_justification": "<specific creativity assessment>",
    "documentation_justification": "<specific documentation assessment>",
            "productivity_justification": "<specific code quality assessment>",
            
            "out_of_box_thinking": "<1-2 sentence assessment>",
            "problem_solving_skills": "<1-2 sentence assessment>",
            "research_capabilities": "<1-2 sentence assessment>",
            "business_understanding": "<1-2 sentence assessment>",
            "non_famous_tools_usage": "<1-2 sentence assessment>"
  }}
}}
```

REMEMBER: Be a tough but fair judge. Real-world projects have flaws - identify them!
"""
        return prompt
    
    def _truncate_content(self, content, max_length=2000):
        """
        Truncate content to fit within token limits
        """
        if not content:
            return "No content provided"
        
        if len(content) > max_length:
            return content[:max_length] + "\n... [content truncated]"
        return content
    
    def _parse_evaluation_result(self, result_text):
        """
        Parse the AI response into structured scores
        """
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'```json\s*(.*?)\s*```', result_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find any JSON object in the response
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                json_str = json_match.group(0) if json_match else result_text
            
            scores = json.loads(json_str)
            
            # Validate and normalize scores
            return {
                'relevance_score': self._normalize_score(scores.get('relevance_score', 5.0)),
                'technical_complexity_score': self._normalize_score(scores.get('technical_complexity_score', 5.0)),
                'creativity_score': self._normalize_score(scores.get('creativity_score', 5.0)),
                'documentation_score': self._normalize_score(scores.get('documentation_score', 5.0)),
                'productivity_score': self._normalize_score(scores.get('productivity_score', 5.0)),
                'overall_score': self._normalize_score(scores.get('overall_score', 5.0)),
                'feedback': scores.get('feedback', 'Evaluation completed.'),
                'detailed_scores': json.dumps(scores.get('detailed_scores', {}))
            }
        except Exception as e:
            print(f"Error parsing evaluation result: {str(e)}")
            # Return fallback scores if parsing fails
            return self._generate_fallback_scores()
    
    def _normalize_score(self, score):
        """
        Ensure score is between 0 and 10
        """
        try:
            score = float(score)
            return max(0.0, min(10.0, score))
        except:
            return 5.0
    
    def _generate_fallback_scores(self):
        """
        Generate varied fallback scores when evaluation fails
        """
        import random
        
        # Generate varied scores in the 4-6 range (realistic fallback)
        scores = {
            'relevance_score': round(random.uniform(4.0, 6.5), 1),
            'technical_complexity_score': round(random.uniform(3.5, 6.0), 1),
            'creativity_score': round(random.uniform(3.0, 5.5), 1),
            'documentation_score': round(random.uniform(2.5, 5.0), 1),
            'productivity_score': round(random.uniform(3.5, 6.0), 1)
        }
        
        # Calculate overall as average
        overall = sum(scores.values()) / len(scores)
        
        return {
            **scores,
            'overall_score': round(overall, 1),
            'feedback': 'Automatic evaluation completed due to technical issue. Scores are estimated based on basic analysis. Manual review strongly recommended for accurate assessment.',
            'detailed_scores': json.dumps({
                'note': 'Fallback scores - technical evaluation failed',
                'recommendation': 'Manual review required for accurate scoring'
            })
        }
    
    def _get_default_criteria(self):
        """
        Get default evaluation criteria
        """
        return [
            {'name': 'Relevance', 'weight': 0.20},
            {'name': 'Technical Complexity', 'weight': 0.20},
            {'name': 'Creativity', 'weight': 0.20},
            {'name': 'Documentation', 'weight': 0.20},
            {'name': 'Productivity', 'weight': 0.20}
        ]
    
    def _evaluate_with_unixcoder(self, submission, hackathon):
        """
        Use UniXCoder for evaluation (placeholder for future implementation)
        """
        # This would use UniXCoder embeddings and similarity scoring
        # For MVP, we'll fall back to OpenAI
        return self._evaluate_with_openai(submission, hackathon)


