import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash



def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


if __name__ == '__main__':
    print(min(3,4))