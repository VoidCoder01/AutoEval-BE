import os
import zipfile
import shutil
from werkzeug.utils import secure_filename
from config import Config

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def extract_code_from_files(file_paths):
    """Extract code content from uploaded files"""
    code_content = []
    
    for file_path in file_paths:
        if not os.path.exists(file_path):
            continue
            
        try:
            # Handle zip files
            if file_path.endswith('.zip'):
                code_content.extend(extract_from_zip(file_path))
            else:
                # Try to read as text
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    code_content.append(f"# File: {os.path.basename(file_path)}\n{content}\n")
        except Exception as e:
            print(f"Error reading file {file_path}: {str(e)}")
    
    return "\n\n".join(code_content)

def extract_from_zip(zip_path):
    """Extract code files from a zip archive"""
    extracted_content = []
    extract_dir = zip_path + '_extracted'
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Read all files from extracted directory
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                file_path = os.path.join(root, file)
                if allowed_file(file):
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            relative_path = os.path.relpath(file_path, extract_dir)
                            extracted_content.append(f"# File: {relative_path}\n{content}\n")
                    except Exception as e:
                        print(f"Error reading extracted file {file_path}: {str(e)}")
        
        # Clean up extracted directory
        shutil.rmtree(extract_dir, ignore_errors=True)
        
    except Exception as e:
        print(f"Error extracting zip file {zip_path}: {str(e)}")
    
    return extracted_content

def extract_documentation(file_paths, project_description):
    """Extract documentation from files (README, .md files, etc.)"""
    doc_content = [f"Project Description:\n{project_description}\n\n"]
    
    for file_path in file_paths:
        if not os.path.exists(file_path):
            continue
            
        filename = os.path.basename(file_path).lower()
        
        # Look for documentation files
        if any(doc in filename for doc in ['readme', '.md', 'doc', '.txt']):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    doc_content.append(f"# {os.path.basename(file_path)}\n{content}\n")
            except Exception as e:
                print(f"Error reading doc file {file_path}: {str(e)}")
    
    return "\n\n".join(doc_content)

def create_upload_folder():
    """Create upload folder if it doesn't exist"""
    if not os.path.exists(Config.UPLOAD_FOLDER):
        os.makedirs(Config.UPLOAD_FOLDER)

def save_uploaded_file(file, submission_id):
    """Save uploaded file and return path"""
    create_upload_folder()
    
    filename = secure_filename(file.filename)
    submission_folder = os.path.join(Config.UPLOAD_FOLDER, f'submission_{submission_id}')
    
    if not os.path.exists(submission_folder):
        os.makedirs(submission_folder)
    
    file_path = os.path.join(submission_folder, filename)
    file.save(file_path)
    
    return file_path

