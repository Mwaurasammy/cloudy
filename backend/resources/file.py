from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, File, Folder  # Assuming Folder model is imported
import base64
from datetime import datetime


file_bp = Blueprint('file', __name__)


@file_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    data = request.get_json()


    if 'folder_id' not in data or 'content' not in data or 'name' not in data:
        return jsonify(error="Missing folder_id, content, or name"), 400


    folder_id = data['folder_id']
    content = data['content']
    name = data['name']


    user_id = get_jwt_identity()
    folder = Folder.query.filter_by(id=folder_id, user_id=user_id).first()


    if not folder:
        return jsonify(error="Folder not found or doesn't belong to the current user"), 404


    file_content = content.encode()
    file = File(name=name, content=file_content, folder_id=folder_id)


    db.session.add(file)
    db.session.commit()


    return jsonify(message="File uploaded", file_id=file.id), 201




@file_bp.route('/list', methods=['GET'])
@jwt_required()
def list_files():
    user_id = get_jwt_identity()
    folder_id = request.args.get('folder_id')
    sort_by_recent = request.args.get('recent', 'false').lower() == 'true'


    if folder_id:
        files_query = File.query.join(Folder).filter(Folder.user_id == user_id, File.folder_id == folder_id)
    else:
        files_query = File.query.join(Folder).filter(Folder.user_id == user_id)


    if sort_by_recent:
        files_query = files_query.order_by(File.last_accessed.desc())


    files = files_query.all()
    file_data = [{"id": f.id, "name": f.name, "folder_id": f.folder_id, "last_accessed": f.last_accessed.isoformat()} for f in files]


    return jsonify(files=file_data), 200




@file_bp.route('/get/<int:file_id>', methods=['GET'])
@jwt_required()
def get_file(file_id):
    user_id = get_jwt_identity()
    file = File.query.join(Folder).filter(File.id == file_id, Folder.user_id == user_id).first()


    if not file:
        return jsonify(error="File not found or doesn't belong to the current user"), 404


    # Update last accessed timestamp
    file.last_accessed = datetime.utcnow()
    db.session.commit()


    return jsonify(file.to_dict()), 200




@file_bp.route('/<int:file_id>', methods=['DELETE'])
@jwt_required()
def delete_file(file_id):
    user_id = get_jwt_identity()
    file = File.query.filter_by(id=file_id, user_id=user_id, deleted_at=None).first()
    if file:
        file.deleted_at = datetime.utcnow()  # Mark as deleted by setting deleted_at
        db.session.commit()
        return jsonify(message="Folder moved to trash"), 200
    return jsonify(error="Folder not found or access denied"), 404




@file_bp.route('/update_name/<int:file_id>', methods=['PUT'])
@jwt_required()
def update_file_name(file_id):
    user_id = get_jwt_identity()
    file = File.query.filter_by(id=file_id).first()


    if not file:
        return jsonify({"error": "File not found"}), 404


    folder = file.folder
    if folder.user_id != user_id:
        return jsonify({"error": "You do not have permission to update this file"}), 403


    data = request.get_json()
    new_name = data.get("new_name")


    if not new_name:
        return jsonify({"error": "New file name is required"}), 400


    file.name = new_name
    db.session.commit()


    return jsonify({"message": "File name updated successfully", "file_id": file.id, "new_name": file.name}), 200




#To list recent files:
# GET /list?recent=true


#To retrieve and update the access timestamp of a specific file:
# GET /get/<file_id>
