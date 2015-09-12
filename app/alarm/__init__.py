from flask import Blueprint

alarm = Blueprint('alarm', __name__)

from . import views
