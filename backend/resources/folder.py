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
    folder_data = [folder.to_dict() for folder in folders]  # Use the `to_dict()` method here
    return jsonify(folders=folder_data), 200


@folder_bp.route('/<int:folder_id>', methods=['PUT'])
@jwt_required()
def update_folder(folder_id):
    user_id = get_jwt_identity()
    data = request.get_json()

    # Retrieve the folder by ID and check ownership
    folder = Folder.query.filter_by(id=folder_id, user_id=user_id).first()
    if not folder:
        return jsonify(error="Folder not found or access denied"), 404

    # Update folder details
    if 'name' in data:
        folder.name = data['name']

    db.session.commit()
    return jsonify(message="Folder updated", folder_id=folder.id, name=folder.name), 200


@folder_bp.route('/<int:folder_id>', methods=['DELETE'])
@jwt_required()
def delete_folder(folder_id):
    folder = Folder.query.get(folder_id)
    if folder:
        db.session.delete(folder)
        db.session.commit()
        return jsonify(message="Folder delete"), 200
    return jsonify(error="folder deleted"), 404