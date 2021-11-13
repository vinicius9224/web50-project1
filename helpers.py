import csv
import urllib.request

from flask import redirect, render_template, request, session,flash
from functools import wraps


def login_required(f):
 
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
          flash(" debes iniciar sesion bro :c")
          return render_template("results.html")
        return f(*args, **kwargs)
    return decorated_function

