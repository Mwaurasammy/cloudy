from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Upload, User  # Ensure User is imported to validate user_id
from supabase_client import upload_file_to_storage  # Your custom Supabase client

# Create a Blueprint for upload-related routes
upload_bp = Blueprint('upload_bp', __name__)

# Route to upload a file
@upload_bp.route('/upload_file', methods=['POST'])
@jwt_required()  # Ensure the user is authenticated with a valid JWT
def upload_file_route():
    # Extract the user_id from the JWT token
    user_id = get_jwt_identity()

    # Check if the file is part of the request
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "File is required"}), 400

    # Get file details
    file_name = file.filename
    file_content = file.read()

    # Upload the file to Supabase (ensure upload_file_to_storage handles file storage)
    upload_response = upload_file_to_storage(file_name, file_content, user_id)
    print(upload_response)
    
    if not upload_response:
        return jsonify({"error": "Failed to upload file"}), 500

    # Assuming upload_response contains a file_path or URL for the uploaded file
    file_path = upload_response.get('file_path')  # Adjust based on actual response

    # Save the file metadata to the database
    try:
        new_upload = Upload(file_name=file_name, user_id=user_id, file_path=file_path)
        db.session.add(new_upload)
        db.session.commit()
        
        db.session.refresh(new_upload)
        
        file_metadata = {
            "file_name": file_name,
            "user_id": user_id,
            "file_path": file_path,  # Include the file path from Supabase
            "storage_response": upload_response
        }

        return jsonify(file_metadata), 200  # Return file metadata on success

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to save metadata: {str(e)}"}), 500

# Route to save file metadata to the database (if needed)
@upload_bp.route('/save_metadata', methods=['POST'])
def save_metadata():
    data = request.json

    # Extract metadata from the request
    file_name = data.get('file_name')
    user_id = data.get('user_id')

    # Validate inputs
    if not file_name or not user_id:
        return jsonify({"error": "File name and user ID are required"}), 400
    if not User.query.get(user_id):  # Validate that the user exists
        return jsonify({"error": "Invalid user ID"}), 400

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

# Add CORS headers to support cross-origin requests
@upload_bp.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response
