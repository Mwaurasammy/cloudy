from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, File, Folder
from datetime import datetime
from supabase_client import (
    upload_file_to_storage,
    delete_file_from_storage,
    rename_file_in_storage,
    move_folder_to_folder,
    view_file_info as get_file_info_from_storage
)

file_bp = Blueprint('file', __name__)

# 1. Upload a file (No folder ID required)
@file_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    if 'file' not in request.files or 'name' not in request.form:
        return jsonify(error="Missing file or name"), 400

    file = request.files['file']
    name = request.form['name']

    user_id = get_jwt_identity()
    file_content = file.read()

    try:
        # Upload the file directly to Supabase storage (without folder)
        file_metadata = upload_file_to_storage(name, file_content)
        if not file_metadata:
            return jsonify(error="Failed to upload file to Supabase Storage"), 500
    except Exception as e:
        return jsonify(error="Failed to upload file to storage", details=str(e)), 500

    return jsonify(message="File uploaded successfully", file=file_metadata), 201

# 2. Update file name
@file_bp.route('/update_name/<int:file_id>', methods=['PUT'])
@jwt_required()
def update_file_name(file_id):
    user_id = get_jwt_identity()
    file = File.query.filter_by(id=file_id, user_id=user_id).first()

    if not file:
        return jsonify({"error": "File not found"}), 404

    if 'new_name' not in request.form:
        return jsonify({"error": "New file name is required"}), 400

    new_name = request.form['new_name']

    try:
        rename_file_in_storage(file.name, new_name)
    except Exception as e:
        return jsonify(error="Failed to rename file in storage", details=str(e)), 500

    file.name = new_name
    db.session.commit()

    return jsonify({"message": "File name updated successfully", "file_id": file.id, "new_name": file.name}), 200

# 3. Delete file (soft delete)
@file_bp.route('/<int:file_id>', methods=['DELETE'])
@jwt_required()
def delete_file(file_id):
    user_id = get_jwt_identity()

    # Find the file in the database
    file = File.query.filter_by(id=file_id, user_id=user_id, deleted_at=None).first()

    if not file:
        return jsonify({"error": "File not found or access denied"}), 404

    # Soft delete the file by marking it in the database
    file.deleted_at = datetime.utcnow()
    db.session.commit()

    # Delete the file from Supabase storage
    try:
        delete_file_from_storage(file.name)
    except Exception as e:
        return jsonify(error="Failed to delete file from storage", details=str(e)), 500

    return jsonify(message="File moved to trash"), 200


# 4. Move file into another folder
@file_bp.route('/move/<int:file_id>', methods=['PUT'])
@jwt_required()
def move_file(file_id):
    user_id = get_jwt_identity()
    file = File.query.filter_by(id=file_id, user_id=user_id).first()

    if not file:
        return jsonify({"error": "File not found"}), 404

    if 'new_folder_id' not in request.form:
        return jsonify({"error": "New folder ID is required"}), 400

    new_folder_id = request.form['new_folder_id']
    new_folder = Folder.query.filter_by(id=new_folder_id, user_id=user_id).first()

    if not new_folder:
        return jsonify({"error": "New folder not found"}), 404

    try:
        move_folder_to_folder(file.name, new_folder.name)  # Updated function call
    except Exception as e:
        return jsonify(error="Failed to move file in storage", details=str(e)), 500

    file.folder_id = new_folder_id
    db.session.commit()

    return jsonify(message="File moved successfully"), 200

# 5. View file info
@file_bp.route('/<int:file_id>/info', methods=['GET'])
@jwt_required()
def view_file_info(file_id):
    user_id = get_jwt_identity()
    file = File.query.filter_by(id=file_id, user_id=user_id).first()

    if not file:
        return jsonify({"error": "File not found"}), 404

    try:
        file_info = get_file_info_from_storage(file.name)
    except Exception as e:
        return jsonify(error="Failed to retrieve file info from storage", details=str(e)), 500

    return jsonify(file_info=file_info), 200

# 6. Get all files
@file_bp.route('/all', methods=['GET'])
@jwt_required()
def get_all_files():
    user_id = get_jwt_identity()

    # Retrieve all files belonging to the logged-in user
    files = File.query.filter_by(user_id=user_id, deleted_at=None).all()

    # Convert file objects to dictionaries
    file_list = [file.to_dict() for file in files]

    return jsonify(files=file_list), 200
