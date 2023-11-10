from functools import wraps
from flask import abort,current_app
from flask_login import current_user
from .models import Permission
from datetime import datetime

def debuggeri(f):
    @wraps(f)
    def wrapper(*args,**kwargs):
        if current_app.config['DEBUG']:
            now = datetime.now()
            msg = now.strftime("%Y-%m-%d %H:%M:%S") + ' '
            msg += f.__name__ + ' '
            if args:
                msg += ''.join(args)
            if kwargs:
                msg += '' + str(kwargs)[1:-1].replace(': ', ':')
            tulos = f(*args, **kwargs)
            msg = msg.rstrip() + ", tulos: " + tulos
            with open("debug_log.txt", "a", encoding="utf-8") as tiedosto:
                tiedosto.write(msg + "\n") 
            # tiedosto.close() 
            # print(msg + "\n")
        else:
            tulos = f(*args,**kwargs)
        return tulos
    return wrapper


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    return permission_required(Permission.ADMIN)(f)

