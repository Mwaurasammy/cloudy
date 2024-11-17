from flask import Blueprint, request, jsonify
from models import db, Upload
# from utils import upload_file
from config import Config
from supabase_client import upload_file_to_storage 

# Create a Blueprint for upload-related routes
upload_bp = Blueprint('upload_bp', __name__)

@upload_bp.route('/upload_file', methods=['POST'])
def upload_file_route():
    data = request.files
    file = data.get('file')  # Fetch the file from the form data
    
    # Check if the file exists in the request
    if not file:
        return jsonify({"error": "File is required"}), 400

    # If the file exists, proceed with creating the file path
    file_name = file.filename
    file_content = file.read()

    # Upload to Supabase
    upload_response = upload_file_to_storage(file_name, file_content)  # Call the function from supabaseclient.py

    if not upload_response:
        return jsonify({"error": "Failed to upload file"}), 500

    # Optionally, save metadata to the database here if needed (you already have a save_metadata route for that)
    file_metadata = upload_response
    return jsonify(file_metadata), 200  # Return file metadata on success

# Route to save file metadata to the database
@upload_bp.route('/save_metadata', methods=['POST'])
def save_metadata():
    data = request.json

    # Extract metadata from the request
    file_name = data.get('file_name')
    user_id = data.get('user_id')

    if not file_name or not user_id:
        return jsonify({"error": "File name and user ID are required"}), 400

    # Create a new Upload instance
    new_upload = Upload(file_name=file_name, user_id=user_id)

    try:
        # Add and commit the new record to the database
        db.session.add(new_upload)
        db.session.commit()
        return jsonify({"status": "Metadata saved successfully", "file_name": file_name, "user_id": user_id}), 200
    except Exception as e:
        # Rollback if there’s an error during commit
        db.session.rollback()
        return jsonify({"error": f"Failed to save metadata: {str(e)}"}), 500

@upload_bp.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response
