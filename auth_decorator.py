from flask import session, redirect
from functools import wraps
from flask import request

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print(dict(session))
        user = dict(session).get('user', None)
        # You would add a check here and usethe user id or something to fetch
        # the other data for that user/check if they exist
        if user:
            if("url" in session):
                del session["url"]
            return f(*args, **kwargs)
        session["url"] = request.url
        return redirect("/login")
    return decorated_function


def bar_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print(dict(session))
        user = dict(session).get('user', None)
        # You would add a check here and usethe user id or something to fetch
        # the other data for that user/check if they exist
        if not user:
            return redirect("/")
        if(user["bar"]):
            return f(*args, **kwargs)
        return redirect("/")
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print(dict(session))
        user = dict(session).get('user', None)
        # You would add a check here and usethe user id or something to fetch
        # the other data for that user/check if they exist
        if not user:
            return redirect("/")
        if(user["admin"]):
            return f(*args, **kwargs)
        return redirect("/")
    return decorated_function