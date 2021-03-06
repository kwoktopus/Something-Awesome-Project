from flask import Flask
from flask_login import LoginManager
from LoginSystems.BadLoginSystem.UserManager import UserManager

app = Flask(__name__, template_folder='../HTMLTemplates')
app.config.from_object("LoginSystems.config")

loginManager = LoginManager(app)
loginManager.login_view = 'login'
userManager = UserManager()

@loginManager.user_loader
def load_user(id):
    """
    Returns a User as specified by their User ID. This function is required by
    flask-login.
    :param id: The UID used to specify a particular User.
    :return: A User matching a specific UID. If no matches are found, returns None.
    """

    return userManager.getUser(int(id))
        

from LoginSystems.BadLoginSystem import routes

