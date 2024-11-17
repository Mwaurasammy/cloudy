from flask import Flask
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from config import Config
from models import db
from flask_cors import CORS



app = Flask(__name__)
CORS(app)
app.config.from_object(Config)
db.init_app(app)
jwt = JWTManager(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Import and register blueprints here
from resources.auth import auth_bp 
from resources.folder import folder_bp
from resources.file import file_bp
from resources.trash import trash_bp
from resources.recents import recents_bp
from resources.uploads import upload_bp


app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(folder_bp, url_prefix='/api/folders')
app.register_blueprint(file_bp, url_prefix='/api/files')
app.register_blueprint(trash_bp, url_prefix='/api/trash')
app.register_blueprint(recents_bp, url_prefix='/api/recents')
app.register_blueprint(upload_bp, url_prefix='/api/upload')

# Database initialization
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
