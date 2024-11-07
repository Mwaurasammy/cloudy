from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, File, Folder  # Assuming Folder model is imported
import base64

file_bp = Blueprint('file', __name__)

@file_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    # Get the data from the incoming request
    data = request.get_json()

    # Validate required fields
    if 'folder_id' not in data or 'content' not in data or 'name' not in data:
        return jsonify(error="Missing folder_id, content, or name"), 400

    folder_id = data['folder_id']
    content = data['content']
    name = data['name']

    # Ensure the folder belongs to the current user
    user_id = get_jwt_identity()
    folder = Folder.query.filter_by(id=folder_id, user_id=user_id).first()

    if not folder:
        return jsonify(error="Folder not found or doesn't belong to the current user"), 404

    # Create the file object and add it to the database
    file_content = content.encode()  # Assuming 'content' is text data
    file = File(name=name, content=file_content, folder_id=folder_id)

    db.session.add(file)
    db.session.commit()

    return jsonify(message="File uploaded", file_id=file.id), 201


@file_bp.route('/list', methods=['GET'])
@jwt_required()
def list_files():
    user_id = get_jwt_identity()  # Get the authenticated user's ID

    # Get the folder_id from query parameters (optional)
    folder_id = request.args.get('folder_id')

    # If folder_id is provided, filter files by folder and user (through the Folder's user_id)
    if folder_id:
        files = File.query.join(Folder).filter(Folder.user_id == user_id, File.folder_id == folder_id).all()
    else:
        # Otherwise, return all files belonging to the user (by filtering through Folder's user_id)
        files = File.query.join(Folder).filter(Folder.user_id == user_id).all()

    # Prepare the list of files to return
    file_data = [{"id": f.id, "name": f.name, "folder_id": f.folder_id} for f in files]

    return jsonify(files=file_data), 200



@file_bp.route('/<int:file_id>', methods=['DELETE'])
@jwt_required()
def delete_file(file_id):
    file = File.query.get(file_id)
    if file:
        db.session.delete(file)
        db.session.commit()
        return jsonify(message="File deleted"), 200
    return jsonify(error="File not found"), 404



@file_bp.route('/update_name/<int:file_id>', methods=['PUT'])
@jwt_required()
def update_file_name(file_id):
    # Get the user ID from the JWT token
    user_id = get_jwt_identity()
    
    # Find the file by ID
    file = File.query.filter_by(id=file_id).first()
    
    # Check if file exists
    if not file:
        return jsonify({"error": "File not found"}), 404
    
    # Optional: Verify that the file belongs to the user (if needed)
    # This assumes you have a relationship linking files to a user indirectly via folders
    folder = file.folder
    if folder.user_id != user_id:
        return jsonify({"error": "You do not have permission to update this file"}), 403
    
    # Get the new name from the request data
    data = request.get_json()
    new_name = data.get("new_name")
    
    # Check if new_name was provided
    if not new_name:
        return jsonify({"error": "New file name is required"}), 400
    
    # Update the file name
    file.name = new_name
    db.session.commit()
    
    return jsonify({"message": "File name updated successfully", "file_id": file.id, "new_name": file.name}), 200
