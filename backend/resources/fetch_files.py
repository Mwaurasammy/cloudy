import os
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Folder, File, Upload
from supabase import create_client

# Initialize Supabase client using environment variables
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
SUPABASE_BUCKET = os.getenv('SUPABASE_BUCKET')
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Create the Blueprint for file-related routes
all_files_bp = Blueprint('all_files', __name__)

# Route to fetch all files for the authenticated user
@all_files_bp.route('/list_files', methods=['GET'])
@jwt_required()  # Require authentication
def get_files():
    try:
        # Get the current user ID from the JWT token
        user_id = get_jwt_identity()

        # Fetch files directly uploaded by the user
        uploads = Upload.query.filter_by(user_id=user_id).all()
        user_files = []

        # Add uploaded files to the list
        for upload in uploads:
            user_files.append({
                'name': upload.file_name,
                'type': 'file',
                'location': 'home',  # These files are not inside folders
                'storage_path': upload.file_path
            })

        # Fetch files in folders belonging to the user
        folders = Folder.query.filter_by(user_id=user_id).all()

        for folder in folders:
            # Get files in each folder
            files_in_folder = File.query.filter_by(folder_id=folder.id).all()
            for file in files_in_folder:
                user_files.append({
                    'name': file.name,
                    'type': 'file',
                    'location': folder.name,  # Folder name as location
                    'storage_path': file.storage_path
                })

        return jsonify(user_files), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
