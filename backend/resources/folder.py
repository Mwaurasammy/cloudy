from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Folder

folder_bp = Blueprint('folder', __name__)

@folder_bp.route('/create', methods=['POST'])
@jwt_required()
def create_folder():
    user_id = get_jwt_identity()
    data = request.get_json()
    folder = Folder(name=data['name'], user_id=user_id)
    db.session.add(folder)
    db.session.commit()
    return jsonify(message="Folder created", folder_id=folder.id), 201

@folder_bp.route('/list', methods=['GET'])
@jwt_required()
def list_folders():
    user_id = get_jwt_identity()
    folders = Folder.query.filter_by(user_id=user_id).all()
    
    # Update last_accessed for each accessed folder
    for folder in folders:
        folder.last_accessed = datetime.utcnow()
    
    db.session.commit()
    
    folder_data = [folder.to_dict() for folder in folders]
    return jsonify(folders=folder_data), 200

@folder_bp.route('/<int:folder_id>', methods=['PUT'])
@jwt_required()
def update_folder(folder_id):
    user_id = get_jwt_identity()
    data = request.get_json()

    folder = Folder.query.filter_by(id=folder_id, user_id=user_id).first()
    if not folder:
        return jsonify(error="Folder not found or access denied"), 404

    # Update folder details
    if 'name' in data:
        folder.name = data['name']

    # Update last_accessed on update
    folder.last_accessed = datetime.utcnow()

    db.session.commit()
    return jsonify(message="Folder updated", folder_id=folder.id, name=folder.name), 200

@folder_bp.route('/<int:folder_id>', methods=['DELETE'])
@jwt_required()
def delete_folder(folder_id):
    user_id = get_jwt_identity()
    folder = Folder.query.filter_by(id=folder_id, user_id=user_id, deleted_at=None).first()
    if folder:
        folder.deleted_at = datetime.utcnow()  # Mark as deleted by setting deleted_at
        db.session.commit()
        return jsonify(message="Folder moved to trash"), 200
    return jsonify(error="Folder not found or access denied"), 404


@folder_bp.route('/recent', methods=['GET'])
@jwt_required()
def get_recent_folders():
    user_id = get_jwt_identity()
    
    # Retrieve folders belonging to the user, sorted by last_accessed in descending order
    recent_folders = Folder.query.filter_by(user_id=user_id).order_by(Folder.last_accessed.desc()).limit(10).all()
    
    # Serialize folder data
    folder_data = [folder.to_dict() for folder in recent_folders]
    
    return jsonify(folders=folder_data), 200