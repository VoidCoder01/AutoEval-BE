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
    """Extract code content from uploaded files with smart filtering"""
    code_content = []
    total_size = 0
    max_total_size = 100 * 1024 * 1024  # 10MB limit for code content
    
    for file_path in file_paths:
        if not os.path.exists(file_path):
            continue
            
        try:
            # Handle zip files
            if file_path.endswith('.zip'):
                zip_content, zip_size = extract_from_zip_smart(file_path, max_total_size - total_size)
                code_content.extend(zip_content)
                total_size += zip_size
            else:
                # Check file size before reading - be more generous for project code
                file_size = os.path.getsize(file_path)
                if file_size > 5 * 1024 * 1024:  # Skip files larger than 5MB (very generous)
                    code_content.append(f"# File: {os.path.basename(file_path)} (SKIPPED - too large: {file_size//1024}KB)\n")
                    continue
                
                if total_size + file_size > max_total_size:
                    code_content.append(f"# Remaining files skipped - size limit reached ({max_total_size//1024//1024}MB)\n")
                    break
                
                # Try to read as text
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    code_content.append(f"# File: {os.path.basename(file_path)}\n{content}\n")
                    total_size += len(content)
                    
        except Exception as e:
            print(f"Error reading file {file_path}: {str(e)}")
            code_content.append(f"# File: {os.path.basename(file_path)} (ERROR: {str(e)})\n")
    
    print(f"📊 Code extraction complete: {len(code_content)} files, {total_size//1024}KB total")
    return "\n\n".join(code_content)

def should_skip_directory(dir_path):
    """Check if directory should be skipped - only skip truly irrelevant directories"""
    skip_dirs = {
        # Dependencies and package managers
        'node_modules', 'vendor', 'packages', '.pnpm-store',
        
        # Version control
        '.git', '.svn', '.hg',
        
        # Build outputs and artifacts
        'build', 'dist', 'out', '.next', '.nuxt', 'target', 'bin', 'obj',
        'public/build', 'static/build', 'assets/build',
        
        # Cache and temporary files
        '__pycache__', '.pytest_cache', '.cache', '.parcel-cache',
        '.nyc_output', 'coverage', 'htmlcov',
        'tmp', 'temp', 'logs', 'log',
        
        # IDE and editor files
        '.vscode', '.idea', '.vs', '.sublime-project',
        
        # OS generated files
        '.ds_store', 'thumbs.db',
        
        # Environment and secrets (but keep example files)
        '.env.local', '.env.production'
    }
    
    dir_name = os.path.basename(dir_path).lower()
    
    # Skip hidden directories except important ones
    if dir_name.startswith('.'):
        important_hidden = {'.github', '.gitlab', '.docker', '.vscode', '.idea'}
        return dir_name not in important_hidden
    
    return dir_name in skip_dirs

def should_prioritize_file(file_path):
    """Check if file should be prioritized for extraction"""
    filename = os.path.basename(file_path).lower()
    priority_files = {
        'readme.md', 'readme.txt', 'readme', 'main.py', 'index.js', 
        'app.py', 'server.js', 'package.json', 'requirements.txt',
        'dockerfile', 'docker-compose.yml', 'config.py', 'settings.py'
    }
    return filename in priority_files

def extract_from_zip_smart(zip_path, max_size_remaining):
    """Smart extraction from ZIP with filtering and prioritization"""
    extracted_content = []
    extract_dir = zip_path + '_extracted'
    total_size = 0
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # First pass: collect and prioritize files
        all_files = []
        priority_files = []
        
        for root, dirs, files in os.walk(extract_dir):
            # Skip unwanted directories
            dirs[:] = [d for d in dirs if not should_skip_directory(os.path.join(root, d))]
            
            for file in files:
                file_path = os.path.join(root, file)
                if allowed_file(file):
                    relative_path = os.path.relpath(file_path, extract_dir)
                    
                    # Check file size
                    try:
                        file_size = os.path.getsize(file_path)
                        if file_size > 500 * 1024:  # Skip files larger than 500KB
                            continue
                            
                        file_info = (file_path, relative_path, file_size)
                        
                        if should_prioritize_file(file_path):
                            priority_files.append(file_info)
                        else:
                            all_files.append(file_info)
                    except:
                        continue
        
        # Process priority files first
        for file_path, relative_path, file_size in priority_files:
            if total_size + file_size > max_size_remaining:
                break
                
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    extracted_content.append(f"# File: {relative_path} [PRIORITY]\n{content}\n")
                    total_size += len(content)
            except Exception as e:
                print(f"Error reading priority file {file_path}: {str(e)}")
        
        # Process remaining files
        for file_path, relative_path, file_size in all_files:
            if total_size + file_size > max_size_remaining:
                extracted_content.append(f"# Remaining files skipped - size limit reached\n")
                break
                
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    extracted_content.append(f"# File: {relative_path}\n{content}\n")
                    total_size += len(content)
            except Exception as e:
                print(f"Error reading file {file_path}: {str(e)}")
        
        # Clean up extracted directory
        shutil.rmtree(extract_dir, ignore_errors=True)
        
        print(f"📦 ZIP extraction: {len(extracted_content)} files, {total_size//1024}KB")
        
    except Exception as e:
        print(f"Error extracting zip file {zip_path}: {str(e)}")
    
    return extracted_content, total_size

def extract_from_zip(zip_path):
    """Legacy function for backward compatibility"""
    content, _ = extract_from_zip_smart(zip_path, 10 * 1024 * 1024)
    return content

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


