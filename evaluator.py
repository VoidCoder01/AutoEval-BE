import os
import openai
from openai import OpenAI
import json
import re
from config import Config

class AIEvaluator:
    def __init__(self):
        self.model = Config.EVALUATION_MODEL
        if self.model == 'openai':
            self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
    
    def evaluate_submission(self, submission, hackathon):
        """
        Evaluate a submission based on the hackathon criteria
        """
        if self.model == 'openai':
            return self._evaluate_with_openai(submission, hackathon)
        else:
            return self._evaluate_with_unixcoder(submission, hackathon)
    
    def _evaluate_with_openai(self, submission, hackathon):
        """
        Use OpenAI GPT-4 to evaluate the submission
        """
        evaluation_prompt = self._build_evaluation_prompt(submission, hackathon)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert hackathon judge tasked with evaluating project submissions. You must provide objective, fair, and constructive evaluations."},
                    {"role": "user", "content": evaluation_prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            result_text = response.choices[0].message.content
            return self._parse_evaluation_result(result_text)
            
        except Exception as e:
            print(f"Error in OpenAI evaluation: {str(e)}")
            return self._generate_fallback_scores()
    
    def _build_evaluation_prompt(self, submission, hackathon):
        """
        Build the prompt for AI evaluation
        """
        criteria = json.loads(hackathon.criteria) if hackathon.criteria else self._get_default_criteria()
        
        prompt = f"""
# Hackathon Evaluation Task

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

## Your Task
Please evaluate this submission on the following criteria (score each out of 10):

1. **Relevance**: How well does the project align with the hackathon theme and requirements?
2. **Technical Complexity**: How sophisticated and well-implemented is the technical solution?
3. **Creativity**: How innovative and creative is the approach?
4. **Documentation**: How clear, complete, and professional is the documentation?

## Response Format
Provide your evaluation in the following JSON format:

```json
{{
  "relevance_score": <score 0-10>,
  "technical_complexity_score": <score 0-10>,
  "creativity_score": <score 0-10>,
  "documentation_score": <score 0-10>,
  "overall_score": <average score 0-10>,
  "feedback": "<detailed feedback explaining the scores, highlighting strengths and areas for improvement>",
  "detailed_scores": {{
    "relevance_justification": "<explanation>",
    "technical_justification": "<explanation>",
    "creativity_justification": "<explanation>",
    "documentation_justification": "<explanation>"
  }}
}}
```

Please provide constructive, specific feedback that will help the participants understand their scores.
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
        Generate default scores when evaluation fails
        """
        return {
            'relevance_score': 5.0,
            'technical_complexity_score': 5.0,
            'creativity_score': 5.0,
            'documentation_score': 5.0,
            'overall_score': 5.0,
            'feedback': 'Automatic evaluation completed. Manual review recommended.',
            'detailed_scores': json.dumps({
                'note': 'Default scores assigned. Please review manually.'
            })
        }
    
    def _get_default_criteria(self):
        """
        Get default evaluation criteria
        """
        return [
            {'name': 'Relevance', 'weight': 0.25},
            {'name': 'Technical Complexity', 'weight': 0.25},
            {'name': 'Creativity', 'weight': 0.25},
            {'name': 'Documentation', 'weight': 0.25}
        ]
    
    def _evaluate_with_unixcoder(self, submission, hackathon):
        """
        Use UniXCoder for evaluation (placeholder for future implementation)
        """
        # This would use UniXCoder embeddings and similarity scoring
        # For MVP, we'll fall back to OpenAI
        return self._evaluate_with_openai(submission, hackathon)

