from flask import Blueprint

radio = Blueprint('radio', __name__)

from . import views