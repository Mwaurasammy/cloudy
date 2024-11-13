from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Folder
from datetime import datetime
from supabase_client import upload_folder_to_storage, rename_folder_in_storage, move_folder_to_folder, delete_folder_from_storage

folder_bp = Blueprint('folder', __name__)

# 1. Create a new folder
@folder_bp.route('/create', methods=['POST'])
@jwt_required()
def create_folder():
    user_id = get_jwt_identity()
    data = request.get_json()

    # Check if the folder name is provided
    if 'name' not in data:
        return jsonify(error="Folder name is required"), 400

    folder_name = data['name']

    # Create a new folder in the database
    folder = Folder(name=folder_name, user_id=user_id)
    db.session.add(folder)
    db.session.commit()

    # Optionally, upload folder to Supabase storage (if required)
    upload_folder_to_storage(folder_name, 'path/to/folder')

    return jsonify(message="Folder created", folder_id=folder.id), 201

# 2. Rename an existing folder
@folder_bp.route('/update_name/<int:folder_id>', methods=['PUT'])
@jwt_required()
def rename_folder(folder_id):
    user_id = get_jwt_identity()

    # Find the folder in the database
    folder = Folder.query.filter_by(id=folder_id, user_id=user_id).first()

    if not folder:
        return jsonify({"error": "Folder not found or access denied"}), 404

    data = request.get_json()
    new_name = data.get("new_name")

    if not new_name:
        return jsonify({"error": "New folder name is required"}), 400

    # Rename the folder in Supabase storage
    rename_folder_in_storage(folder.name, new_name)

    # Update the folder name in the database
    folder.name = new_name
    db.session.commit()

    return jsonify({"message": "Folder name updated successfully", "folder_id": folder.id, "new_name": folder.name}), 200

# 3. Move a folder to another folder
@folder_bp.route('/move/<int:folder_id>', methods=['PUT'])
@jwt_required()
def move_folder(folder_id):
    user_id = get_jwt_identity()

    # Find the folder in the database
    folder = Folder.query.filter_by(id=folder_id, user_id=user_id).first()

    if not folder:
        return jsonify({"error": "Folder not found or access denied"}), 404

    data = request.get_json()
    target_folder_id = data.get("target_folder_id")

    # Find the target folder
    target_folder = Folder.query.filter_by(id=target_folder_id, user_id=user_id).first()

    if not target_folder:
        return jsonify({"error": "Target folder not found"}), 404

    # Move the folder in Supabase storage
    move_folder_to_folder(folder.name, target_folder.name)

    return jsonify(message="Folder moved successfully"), 200

# 4. Delete a folder (soft delete in DB and delete from Supabase)
@folder_bp.route('/<int:folder_id>', methods=['DELETE'])
@jwt_required()
def delete_folder(folder_id):
    user_id = get_jwt_identity()

    # Find the folder in the database
    folder = Folder.query.filter_by(id=folder_id, user_id=user_id, deleted_at=None).first()

    if not folder:
        return jsonify({"error": "Folder not found or access denied"}), 404

    # Soft delete the folder by marking it in the database
    folder.deleted_at = datetime.utcnow()
    db.session.commit()

    # Delete the folder from Supabase storage
    delete_folder_from_storage(folder.name)

    return jsonify(message="Folder moved to trash"), 200

# 5. View folder info (list of files inside the folder)
@folder_bp.route('/<int:folder_id>/info', methods=['GET'])
@jwt_required()
def view_folder_info(folder_id):
    user_id = get_jwt_identity()

    # Find the folder in the database
    folder = Folder.query.filter_by(id=folder_id, user_id=user_id).first()

    if not folder:
        return jsonify({"error": "Folder not found or access denied"}), 404

    # Get the folder info from Supabase
    folder_info = view_folder_info(folder.name)

    return jsonify(folder_info=folder_info), 200