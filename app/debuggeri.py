# Tiedosto: debuggeri.py
import functools
from datetime import datetime
from flask import current_app
DEBUG = current_app.config['DEBUG']
def debuggeri(function):
    @functools.wraps(function)
    def wrapper(*args,**kwargs):
        if DEBUG:
            now = datetime.now()
            msg = now.strftime("%Y-%m-%d %H:%M:%S") + ' '
            msg += function.__name__ + ' '
            if args:
                msg += ''.join(args)
            if kwargs:
                msg += '' + str(kwargs)[1:-1].replace(': ', ':')
            tulos = function(*args)
            msg = msg.rstrip() + ", tulos: " + tulos
            with open("debug_log.txt", "a", encoding="utf-8") as tiedosto:
                tiedosto.write(msg + "\n") 
            # tiedosto.close() 
            # print(msg + "\n")
        else:
            tulos = function(*args)
        return tulos
    return wrapper
