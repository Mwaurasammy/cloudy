from flask import Blueprint, request, jsonify
from models import db, Upload
from utils import get_presigned_url

# Create a Blueprint for upload-related routes
upload_bp = Blueprint('upload_bp', __name__)

# Route to generate a presigned URL for uploading a file
@upload_bp.route('/get_presigned_url', methods=['POST'])
def generate_presigned_url():
    data = request.json
    file_name = data.get('file_name')
    if not file_name:
        return jsonify({"error": "File name is required"}), 400

    print(f"Received file name: {file_name}")  # Log to check if request is coming through

    # Generate a presigned URL using a helper function (e.g., from Supabase or S3)
    presigned_url = get_presigned_url(file_name)
    if not presigned_url:
        return jsonify({"error": "Failed to generate presigned URL"}), 500

    return jsonify({"url": presigned_url, "file_name": file_name})

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

#/upload/get_presigned_url
#/upload/save_metadata