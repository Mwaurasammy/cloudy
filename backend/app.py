from flask import Flask
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from .config import Config
from models import db

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
jwt = JWTManager(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Import and register blueprints here
from resources.auth import auth_bp 
from resources.folder import folder_bp
from resources.file import file_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(folder_bp, url_prefix='/api/folders')
app.register_blueprint(file_bp, url_prefix='/api/files')

# Database initialization
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
