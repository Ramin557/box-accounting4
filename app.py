import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key-for-development")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    # Fallback to sqlite for local development
    database_url = "sqlite:///accounting.db"
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {}
else:
    # PostgreSQL configuration
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }

app.config["SQLALCHEMY_DATABASE_URI"] = database_url

# Initialize the app with the extension
db.init_app(app)

# Import routes after app is configured
from routes import *  # noqa: F401,F403

# Create tables after everything is imported
with app.app_context():
    # Import models to ensure they're registered
    import models  # noqa: F401
    db.create_all()
