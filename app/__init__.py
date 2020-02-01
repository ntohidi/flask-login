from flask import Flask
from flask_login import LoginManager

import os
import pymongo

# def create_app():
app = Flask("LoginApp")

app.config.from_object('config.' + os.environ.get('LOGINAPP_CONFIG_MOD', 'DevLocalConfig'))

app.config['MONGO_DATABASE_URI'] = app.config['DATABASES']['mongo']['url']
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True

print(" * Connecting to MongoDB * " + app.config['DATABASES']['mongo']['dbname'])
db = pymongo.MongoClient(app.config['DATABASES']['mongo']['url'])[app.config['DATABASES']['mongo']['dbname']]

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

from models.User import UserModel


@login_manager.user_loader
def load_user(user_id):
    from bson.objectid import ObjectId
    user = UserModel.get_one(args={"_id": ObjectId(user_id)}, filters={"_id": 0})
    return user


from app.auth.controller import auth as auth_blueprint
from app.main.controller import main as main_blueprint

routes = [
    auth_blueprint,
    main_blueprint
]

for route in routes:
    app.register_blueprint(route)

# app.register_blueprint(auth_blueprint)
# app.register_blueprint(main_blueprint)

# return app
