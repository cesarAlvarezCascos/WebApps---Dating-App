from flask import Flask

# Things to import at the beginning
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager

# Declarations to insert before the create_app function:
class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)


def create_app(test_config=None):
  app = Flask(__name__)

  # A secret for signing session cookies
  app.config["SECRET_KEY"] = "93220d9b340cf9a6c39bac99cce7daf220167498f91fa"

  # Configure the DataBase Connection
  app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://25_webapp_047:K5pdi2yU@mysql.lab.it.uc3m.es/25_webapp_047b"  

  db.init_app(app)


  # INITIALIZE FLASK-Login Module
  login_manager = LoginManager()
  login_manager.login_view = 'auth.login' # vista (ruta) que Flask-Login redirigirá si un usuario no autenticado intenta acceder a una ruta protegida. Usar sign up en el project 
  login_manager.init_app(app)

  from . import model
  @login_manager.user_loader
  def load_user(user_id):
    return db.session.get(model.User, int(user_id))
    
  # REGISTERING BLUEPRINTS
  # (we import main from here to avoid circular imports in the next lab)
  from . import main
  app.register_blueprint(main.bp)

  from . import auth
  app.register_blueprint(auth.bp)

  return app
