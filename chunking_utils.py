"""
Utilities for chunking large code content for AI evaluation
"""

def chunk_text(text, max_chunk_size=3000, overlap=200):
    """
    Split text into overlapping chunks
    
    Args:
        text (str): Text to chunk
        max_chunk_size (int): Maximum characters per chunk
        overlap (int): Number of characters to overlap between chunks
    
    Returns:
        list: List of text chunks
    """
    if len(text) <= max_chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        # Calculate end position
        end = start + max_chunk_size
        
        # If this is not the last chunk, try to break at a natural boundary
        if end < len(text):
            # Look for line breaks near the end
            for i in range(min(100, max_chunk_size // 10)):  # Look back up to 100 chars
                if text[end - i] == '\n':
                    end = end - i + 1  # Include the newline
                    break
        
        # Extract chunk
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move start position (with overlap)
        start = end - overlap if end < len(text) else end
        
        # Prevent infinite loop
        if start >= len(text):
            break
    
    return chunks

def chunk_code_content(code_content, max_chunk_size=3000):
    """
    Intelligently chunk code content, trying to preserve function/class boundaries
    
    Args:
        code_content (str): Code content to chunk
        max_chunk_size (int): Maximum characters per chunk
    
    Returns:
        list: List of code chunks with metadata
    """
    if len(code_content) <= max_chunk_size:
        return [{
            'content': code_content,
            'chunk_id': 1,
            'total_chunks': 1,
            'size': len(code_content)
        }]
    
    # Split by files first (if multiple files are concatenated)
    file_sections = []
    current_section = ""
    
    lines = code_content.split('\n')
    for line in lines:
        # Look for file separators or headers
        if line.startswith('===') or line.startswith('---') or 'File:' in line:
            if current_section.strip():
                file_sections.append(current_section.strip())
            current_section = line + '\n'
        else:
            current_section += line + '\n'
    
    # Add the last section
    if current_section.strip():
        file_sections.append(current_section.strip())
    
    # If no file sections found, treat as single content
    if len(file_sections) <= 1:
        file_sections = [code_content]
    
    # Chunk each file section
    all_chunks = []
    chunk_counter = 1
    
    for section in file_sections:
        if len(section) <= max_chunk_size:
            all_chunks.append({
                'content': section,
                'chunk_id': chunk_counter,
                'size': len(section)
            })
            chunk_counter += 1
        else:
            # Split large sections into smaller chunks
            text_chunks = chunk_text(section, max_chunk_size, overlap=300)
            for chunk_text in text_chunks:
                all_chunks.append({
                    'content': chunk_text,
                    'chunk_id': chunk_counter,
                    'size': len(chunk_text)
                })
                chunk_counter += 1
    
    # Add total_chunks to all chunks
    total_chunks = len(all_chunks)
    for chunk in all_chunks:
        chunk['total_chunks'] = total_chunks
    
    return all_chunks

def create_chunk_summary(chunks):
    """
    Create a summary of all chunks for context
    
    Args:
        chunks (list): List of chunk dictionaries
    
    Returns:
        str: Summary of chunks
    """
    total_size = sum(chunk['size'] for chunk in chunks)
    
    summary = f"""
Code Analysis Summary:
- Total chunks: {len(chunks)}
- Total content size: {total_size:,} characters
- Average chunk size: {total_size // len(chunks):,} characters

Chunk breakdown:
"""
    
    for i, chunk in enumerate(chunks, 1):
        preview = chunk['content'][:100].replace('\n', ' ')
        summary += f"  Chunk {i}: {chunk['size']:,} chars - {preview}...\n"
    
    return summary

def combine_chunk_evaluations(chunk_results):
    """
    Combine evaluation results from multiple chunks
    
    Args:
        chunk_results (list): List of evaluation results from each chunk
    
    Returns:
        dict: Combined evaluation result
    """
    if not chunk_results:
        return {
            'relevance_score': 5.0,
            'technical_complexity_score': 5.0,
            'creativity_score': 5.0,
            'documentation_score': 5.0,
            'productivity_score': 5.0,
            'overall_score': 5.0,
            'feedback': 'No evaluation results to combine.',
            'detailed_scores': '{}'
        }
    
    if len(chunk_results) == 1:
        return chunk_results[0]
    
    # Calculate weighted averages based on chunk sizes
    total_weight = sum(result.get('chunk_weight', 1) for result in chunk_results)
    
    combined_scores = {
        'relevance_score': 0,
        'technical_complexity_score': 0,
        'creativity_score': 0,
        'documentation_score': 0,
        'productivity_score': 0
    }
    
    feedbacks = []
    
    for result in chunk_results:
        weight = result.get('chunk_weight', 1) / total_weight
        
        for score_key in combined_scores:
            combined_scores[score_key] += result.get(score_key, 5.0) * weight
        
        if result.get('feedback'):
            feedbacks.append(f"Chunk {result.get('chunk_id', '?')}: {result['feedback']}")
    
    # Calculate overall score
    overall_score = sum(combined_scores.values()) / len(combined_scores)
    
    # Combine feedback
    combined_feedback = f"""
Multi-chunk evaluation completed ({len(chunk_results)} chunks analyzed):

""" + "\n\n".join(feedbacks)
    
    return {
        'relevance_score': round(combined_scores['relevance_score'], 1),
        'technical_complexity_score': round(combined_scores['technical_complexity_score'], 1),
        'creativity_score': round(combined_scores['creativity_score'], 1),
        'documentation_score': round(combined_scores['documentation_score'], 1),
        'productivity_score': round(combined_scores['productivity_score'], 1),
        'overall_score': round(overall_score, 1),
        'feedback': combined_feedback,
        'detailed_scores': '{"note": "Combined from multiple chunks"}'
    }


