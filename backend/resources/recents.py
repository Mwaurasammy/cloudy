from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, File, Folder
from datetime import datetime

recents_bp = Blueprint('recents', __name__)

# 1. List recent files
@recents_bp.route('/files', methods=['GET'])
@jwt_required()
def list_recent_files():
    user_id = get_jwt_identity()

    # Get all files for the user ordered by the last_accessed field (descending)
    recent_files = File.query.filter_by(user_id=user_id).order_by(File.last_accessed.desc()).limit(10).all()

    files_info = [file.to_dict() for file in recent_files]

    return jsonify(recent_files=files_info), 200

# 2. List recent folders
@recents_bp.route('/folders', methods=['GET'])
@jwt_required()
def list_recent_folders():
    user_id = get_jwt_identity()

    # Get all folders for the user ordered by the last_accessed field (descending)
    recent_folders = Folder.query.filter_by(user_id=user_id).order_by(Folder.last_accessed.desc()).limit(10).all()

    folders_info = [folder.to_dict() for folder in recent_folders]

    return jsonify(recent_folders=folders_info), 200

# 3. Update the last accessed timestamp for a file
@recents_bp.route('/file/<int:file_id>/accessed', methods=['PUT'])
@jwt_required()
def update_file_accessed(file_id):
    user_id = get_jwt_identity()

    # Find the file in the database
    file = File.query.filter_by(id=file_id, user_id=user_id).first()

    if not file:
        return jsonify({"error": "File not found or access denied"}), 404

    # Update the last accessed timestamp
    file.last_accessed = datetime.utcnow()
    db.session.commit()

    return jsonify({"message": "File last accessed timestamp updated"}), 200

# 4. Update the last accessed timestamp for a folder
@recents_bp.route('/folder/<int:folder_id>/accessed', methods=['PUT'])
@jwt_required()
def update_folder_accessed(folder_id):
    user_id = get_jwt_identity()

    # Find the folder in the database
    folder = Folder.query.filter_by(id=folder_id, user_id=user_id).first()

    if not folder:
        return jsonify({"error": "Folder not found or access denied"}), 404

    # Update the last accessed timestamp
    folder.last_accessed = datetime.utcnow()
    db.session.commit()

    return jsonify({"message": "Folder last accessed timestamp updated"}), 200