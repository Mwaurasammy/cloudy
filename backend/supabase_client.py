import os
import logging
import traceback
import mimetypes
from supabase import create_client
from config import Config
from models import db, File
from flask import current_app as app

# Initialize Supabase client
supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
bucket_name = 'bucket'  # Your Supabase bucket name

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Allowed MIME types for uploads
ALLOWED_MIME_TYPES = [
    'image/jpeg',
    'image/png',
    'image/jpg',
    'image/gif',
    'image/svg+xml',
    'application/pdf',
    'text/plain',
    'application/zip'
]

# --- File and Folder Operations ---

# 1. Upload a file to Supabase storage
def upload_file_to_storage(file_name, file_content, user_id):
    try:
        storage = supabase.storage
        
        # Guess MIME type of the file
        mime_type, _ = mimetypes.guess_type(file_name)
        if mime_type not in ALLOWED_MIME_TYPES:
            logging.error(f"Invalid MIME type: {mime_type}")
            return {"error": "Invalid file type"}, 400
        
        # Check if the file already exists in the storage
        file_path = os.path.join('files', file_name)
        file_list = supabase.storage.from_(bucket_name).list('files', {'prefix': file_name})
        if file_list and any(f['name'] == file_name for f in file_list):
            logging.warning(f"File {file_name} already exists")
            return {"error": "File already exists"}, 409

        # Upload file to Supabase storage
        response = storage.from_(bucket_name).upload(file_path, file_content, {"content-type": mime_type})
        
        # Check if the response has an error
        if hasattr(response, 'error') and response.error:
            logging.error(f"Error uploading file {file_name}: {response.error['message']}")
            return {"error": "Storage upload failed"}, 500

        # Save metadata to the database
        with app.app_context():
            new_file = File(name=file_name, storage_path=file_path, user_id=user_id)
            db.session.add(new_file)
            db.session.commit()
            db.session.refresh(new_file)

        logging.info(f"File {file_name} uploaded to Supabase Storage successfully.")
        return {
            "file_path": file_path,
            "message": "File uploaded successfully",
            "data": new_file.to_dict()
        }
    
    except Exception as e:
        logging.error(f"Error during file upload: {e}")
        logging.error(traceback.format_exc())
        return {"error": "Internal server error"}, 500
    
# 2. Upload a folder to Supabase storage
def upload_folder_to_storage(folder_name, folder_path, user_id):
    try:
        storage = supabase.storage
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, folder_path)
                file_name = os.path.join('folders', folder_name, rel_path)
                with open(file_path, 'rb') as f:
                    file_content = f.read()
                    response = storage.from_(bucket_name).upload(file_name, file_content)
                    if response.get('error'):
                        logging.error(f"Error uploading {file_name}: {response['error']['message']}")
                    else:
                        # Save file metadata with user_id
                        new_file = File(
                            name=file_name,
                            storage_path=file_name,  # Storage path in Supabase
                            user_id=user_id  # Include the user_id when saving to the database
                        )
                        db.session.add(new_file)
                        db.session.commit()
        logging.info(f"Folder {folder_name} uploaded successfully.")
        return f"Folder {folder_name} uploaded successfully."
    except Exception as e:
        logging.error(f"Folder upload failed: {e}")
        logging.error(traceback.format_exc())
        return str(e)

# 3. Delete a file from Supabase storage
def delete_file_from_storage(file_name, user_id):
    try:
        storage = supabase.storage
        file_path = os.path.join('files', file_name)
        
        # Check if file belongs to user_id
        file_record = db.session.query(File).filter(File.name == file_name, File.user_id == user_id).first()
        if not file_record:
            return {"error": "File not found for this user."}, 404
        
        response = storage.from_(bucket_name).remove([file_path])
        if response.get('error'):
            logging.error(response['error']['message'])
            return f"Error deleting file {file_name}: {response['error']['message']}"
        
        db.session.delete(file_record)
        db.session.commit()
        logging.info(f"File {file_name} deleted successfully.")
        return f"File {file_name} deleted successfully."
    except Exception as e:
        logging.error(f"File deletion failed: {e}")
        logging.error(traceback.format_exc())
        return str(e)

# 4. Delete a folder and its contents from Supabase storage
def delete_folder_from_storage(folder_name):
    try:
        storage = supabase.storage
        folder_path = os.path.join('folders', folder_name, '')
        files = storage.from_(bucket_name).list(folder_path)
        if not files or 'error' in files:
            logging.error(files.get('error', {}).get('message', 'Unknown error'))
            return f"Error listing folder {folder_name}: {files.get('error', {}).get('message', 'Unknown error')}"

        for file in files['data']:
            storage.from_(bucket_name).remove([file['name']])
        logging.info(f"Folder {folder_name} deleted successfully.")
        return f"Folder {folder_name} and its contents deleted successfully."
    except Exception as e:
        logging.error(f"Folder deletion failed: {e}")
        logging.error(traceback.format_exc())
        return str(e)

# 5. Rename a file in Supabase storage
def rename_file_in_storage(old_name, new_name):
    try:
        storage = supabase.storage
        old_path = os.path.join('files', old_name)
        new_path = os.path.join('files', new_name)
        response = storage.from_(bucket_name).move(old_path, new_path)
        if response.get('error'):
            logging.error(response['error']['message'])
            return f"Error renaming file: {response['error']['message']}"
        logging.info(f"File {old_name} renamed to {new_name} successfully.")
        return f"File {old_name} renamed to {new_name} successfully."
    except Exception as e:
        logging.error(f"Rename failed: {e}")
        logging.error(traceback.format_exc())
        return str(e)

# 6. Rename a folder in Supabase storage
def rename_folder_in_storage(old_folder_name, new_folder_name):
    try:
        storage = supabase.storage
        old_folder_path = os.path.join('folders', old_folder_name, '')
        files = storage.from_(bucket_name).list(old_folder_path)

        for file in files['data']:
            old_file_path = file['name']
            new_file_path = old_file_path.replace(old_folder_name, new_folder_name, 1)
            storage.from_(bucket_name).move(old_file_path, new_file_path)
        logging.info(f"Folder {old_folder_name} renamed to {new_folder_name} successfully.")
        return f"Folder {old_folder_name} renamed to {new_folder_name} successfully."
    except Exception as e:
        logging.error(f"Folder rename failed: {e}")
        logging.error(traceback.format_exc())
        return str(e)

# 7. Move a folder to another folder in Supabase storage
def move_folder_to_folder(folder_name, target_folder_name):
    try:
        storage = supabase.storage
        folder_path = os.path.join('folders', folder_name, '')
        files = storage.from_(bucket_name).list(folder_path)
        if not files or 'error' in files:
            logging.error(files.get('error', {}).get('message', 'Unknown error'))
            return f"Error listing folder {folder_name}: {files.get('error', {}).get('message', 'Unknown error')}"

        for file in files['data']:
            old_file_path = file['name']
            new_file_path = old_file_path.replace(f"folders/{folder_name}/", f"folders/{target_folder_name}/", 1)
            response = storage.from_(bucket_name).move(old_file_path, new_file_path)
            if response.get('error'):
                logging.error(f"Error moving file {old_file_path}: {response['error']['message']}")
        
        logging.info(f"Folder {folder_name} moved to {target_folder_name} successfully.")
        return f"Folder {folder_name} moved to {target_folder_name} successfully."
    except Exception as e:
        logging.error(f"Move folder failed: {e}")
        logging.error(traceback.format_exc())
        return str(e)

# 8. View file information (metadata)
def view_file_info(file_name):
    try:
        storage = supabase.storage
        file_path = os.path.join('files', file_name)
        file_info = storage.from_(bucket_name).get_metadata(file_path)
        if file_info.get('error'):
            return f"Error: {file_info['error']['message']}"
        return file_info.get('data', 'No metadata available')
    except Exception as e:
        logging.error(f"Error fetching file info: {e}")
        logging.error(traceback.format_exc())
        return str(e)

# 9. View folder information (metadata)
def view_folder_info(folder_name):
    try:
        storage = supabase.storage
        folder_path = os.path.join('folders', folder_name, '')
        files = storage.from_(bucket_name).list(folder_path)
        if not files or 'error' in files:
            logging.error(files.get('error', {}).get('message', 'Unknown error'))
            return f"Error: {files.get('error', {}).get('message', 'Unknown error')}"
        return files['data']
    except Exception as e:
        logging.error(f"Error fetching folder info: {e}")
        logging.error(traceback.format_exc())
        return str(e)

