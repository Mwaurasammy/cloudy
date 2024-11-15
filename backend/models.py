from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    folders = db.relationship('Folder', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Folder(db.Model):
    __tablename__ = 'folders'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    files = db.relationship('File', back_populates='folder')  # This should be in Folder model
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)  # New field to track deletion timestamp

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'last_accessed': self.last_accessed.isoformat(),
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
        }


class File(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    storage_path = db.Column(db.String(255), nullable=False)  # Path in the Supabase bucket
    folder_id = db.Column(db.Integer, db.ForeignKey('folders.id'), nullable=True)  # Link to folder
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    folder = db.relationship('Folder', back_populates='files')  # Back-reference to folder

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'storage_path': self.storage_path,
            'created_at': self.created_at.isoformat(),
            'last_accessed': self.last_accessed.isoformat(),
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
            'folder_id': self.folder_id,  # Include folder_id for clarity in the output
        }

class Upload(db.Model):
    __tablename__ = 'uploads'
    
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(255), nullable=False)  # Ensures file_name is always provided
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Links to User model
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)  # Defaults to current timestamp

    # Relationship to the User model
    user = db.relationship('User', backref=db.backref('uploads', lazy=True))

    def to_dict(self):
        """Convert the Upload object to a dictionary format for JSON serialization."""
        return {
            'id': self.id,
            'file_name': self.file_name,
            'user_id': self.user_id,
            'upload_time': self.upload_time.isoformat(),
        }