from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_moment import Moment
from automate.config import Config
import pymysql

# Initializations of imports
db = SQLAlchemy()
mail = Mail()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()
moment = Moment()

login_manager.login_view = 'users.login'
login_manager.login_message_category = 'danger'
login_manager.login_message = 'User Login is Required'

# function to create app
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    moment.init_app(app)

    # Import and Registration of blueprints routes
    from automate.feedmill.routes import feedmill
    from automate.users.routes import users
    from automate.stores.routes import stores

    app.register_blueprint(feedmill)
    app.register_blueprint(users)
    app.register_blueprint(stores)

    return app
