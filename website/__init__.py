from flask import Flask
from flask_login import LoginManager
from flask_pymongo import PyMongo
from pymongo import MongoClient
from os import path
from bson import ObjectId

# Database configurations
DB_NAME = "mongodb"
MONGO_URI = 'mongodb://localhost:27017/' + DB_NAME  # MongoDB connection URI

# Initialize PyMongo
mongo = PyMongo()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'

    # Configure PyMongo
    app.config['MONGO_URI'] = MONGO_URI
    mongo.init_app(app)

    # Register blueprints
    from .views import views
    from .auth import auth
    from .gpt import gpt
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(gpt, url_prefix='/gpt')

    # Import User model
    from .models import User

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        # Assuming you have a 'users' collection in your MongoDB
        user_data = mongo.db.users.find_one({'id': user_id})
        if user_data:
            return User(user_data)
        return None

    return app
