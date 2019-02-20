from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment

db = SQLAlchemy()
bootstrap = Bootstrap()
login_manager = LoginManager()
mail = Mail()
moment = Moment()


login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


@login_manager.user_loader
def load_user(user_id):
   from leap.models import User
   user = User.query.get(int(user_id))
   return user

