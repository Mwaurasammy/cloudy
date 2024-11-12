from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Folder, File
from datetime import datetime, timedelta

trash_bp = Blueprint('trash', __name__)

# Endpoint 1: List all trashed folders
@trash_bp.route('/folders', methods=['GET'])
@jwt_required()
def list_trashed_folders():
    user_id = get_jwt_identity()
    trashed_folders = Folder.query.filter_by(user_id=user_id).filter(Folder.deleted_at.isnot(None)).all()
    folder_data = [folder.to_dict() for folder in trashed_folders]
    return jsonify(folders=folder_data), 200

# Endpoint 2: List all trashed files
@trash_bp.route('/files', methods=['GET'])
@jwt_required()
def list_trashed_files():
    user_id = get_jwt_identity()
    trashed_files = File.query.filter_by(user_id=user_id).filter(File.deleted_at.isnot(None)).all()
    file_data = [file.to_dict() for file in trashed_files]
    return jsonify(files=file_data), 200

# Endpoint 3: Restore a folder from trash
@trash_bp.route('/restore/folder/<int:folder_id>', methods=['PUT'])
@jwt_required()
def restore_folder(folder_id):
    user_id = get_jwt_identity()
    folder = Folder.query.filter_by(id=folder_id, user_id=user_id, deleted_at__isnot=None).first()
    if not folder:
        return jsonify(error="Folder not found or not in trash"), 404
    folder.deleted_at = None
    db.session.commit()
    return jsonify(message="Folder restored", folder_id=folder.id), 200

# Endpoint 4: Restore a file from trash
@trash_bp.route('/restore/file/<int:file_id>', methods=['PUT'])
@jwt_required()
def restore_file(file_id):
    user_id = get_jwt_identity()
    file = File.query.filter_by(id=file_id, user_id=user_id, deleted_at__isnot=None).first()
    if not file:
        return jsonify(error="File not found or not in trash"), 404
    file.deleted_at = None
    db.session.commit()
    return jsonify(message="File restored", file_id=file.id), 200

# Endpoint 5: Permanently delete old trashed folders and files (e.g., older than 30 days)
@trash_bp.route('/cleanup', methods=['DELETE'])
@jwt_required()
def cleanup_old_trashed_items():
    user_id = get_jwt_identity()
    threshold_date = datetime.utcnow() - timedelta(days=30)

    # Delete folders in trash older than 30 days
    old_trashed_folders = Folder.query.filter(Folder.user_id == user_id, Folder.deleted_at <= threshold_date).all()
    for folder in old_trashed_folders:
        db.session.delete(folder)

    # Delete files in trash older than 30 days
    old_trashed_files = File.query.filter(File.user_id == user_id, File.deleted_at <= threshold_date).all()
    for file in old_trashed_files:
        db.session.delete(file)

    db.session.commit()
    return jsonify(message="Old trashed items permanently deleted"), 200

#GET /api/trash/folders
#GET /api/trash/files
#PUT /api/trash/restore/folder/<folder_id>
#PUT /api/trash/restore/file/<file_id>
#DELETE /api/trash/cleanup