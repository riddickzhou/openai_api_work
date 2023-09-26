from flask import Flask
from flask_login import LoginManager
from flask_pymongo import PyMongo
from pymongo import MongoClient
from os import path, environ
from bson import ObjectId
import logging

# Database configurations
DB_NAME = "mongodb"

# Check if DB_ADDR environment variable is defined, if not, revert back to localhost
DB_ADDR = environ.get('DB_ADDR', 'localhost')
MONGO_URI = f"mongodb://{DB_ADDR}:27017/" + DB_NAME  # MongoDB connection URI

# Initialize PyMongo
mongo = PyMongo()

def create_app():
    application = Flask(__name__)
    application.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    # Set debug mode based on FLASK_DEBUG environment variable
    #DEBUG_MODE = environ.get('FLASK_DEBUG', 'False') == 'True'
    application.debug = True
    
    # Set up logging
    if application.debug:
        application.logger.setLevel(logging.DEBUG)
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        application.logger.addHandler(stream_handler)
    else:
        application.logger.setLevel(logging.INFO)
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        application.logger.addHandler(stream_handler)

    # Print a statement to verify logging setup
    application.logger.info("App started in debug mode: {}".format(application.debug))

    # Configure PyMongo
    application.config['MONGO_URI'] = MONGO_URI
    mongo.init_app(application)

    # Register blueprints
    from .views import views
    from .auth import auth
    from .gpt import gpt
    application.register_blueprint(views, url_prefix='/')
    application.register_blueprint(auth, url_prefix='/')
    application.register_blueprint(gpt, url_prefix='/gpt')

    # Import User model
    from .models import User

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(application)

    @login_manager.user_loader
    def load_user(user_id):
        # Assuming you have a 'users' collection in your MongoDB
        user_data = mongo.db.users.find_one({'id': user_id})
        if user_data:
            return User(user_data)
        return None

    return application
