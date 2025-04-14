from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from models import db
from routes import register_blueprints

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize database and migrations
db.init_app(app)
migrate = Migrate(app, db)

# Register Blueprints
register_blueprints(app)

if __name__ == '__main__':
    app.run(debug=True)