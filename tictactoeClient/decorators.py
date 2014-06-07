import inspect
import requests
import time
from functools import wraps


def logger(filename="call_log.txt"):
    """Logs function name and arguments to <filename>"""
    def wrap(f):
        "Log function name and parameters to file call_log.txt"
        @wraps(f)
        def wrapper(*args, **kwargs):
            name = f.__name__
            with open(filename, "a") as output:
                output.write("Called function " + name +
                             " with args: " +
                             (str(args) if args else "None") +
                             ", kwargs: " +
                             (str(kwargs) if kwargs else "None") +
                             "\n")
            return f(*args, **kwargs)
        return wrapper
    return wrap


def execution_time_measurer(filename="execution_time_log.txt"):
    """Logs function execution time to filename"""
    def wrap(f):
        "Log function execution time to file execution_time_log.txt"
        @wraps(f)
        def wrapper(*args, **kwargs):
            start = time.time()
            res = f(*args, **kwargs)
            with open(filename, "a") as output:
                output.write("Function " + f.__name__ +
                             " executed in: " + str(time.time() - start) +
                             " seconds\n")
            return res
        return wrapper
    return wrap


def safe_execution(defaultValue=None):
    """Catches any exceptions and returns defaultValue"""
    def wrap(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as ex:
                print "Exception %s" % ex
                return defaultValue
        return wrapper
    return wrap


def rpc_decorator(url):
    """Call RESTful service at url/method_name/param1/param2/..."""
    def wrap(f):
        def wrapper(*args, **kwargs):
            req_url = '/'.join([url, f.__name__])
            for arg in args:
                req_url = req_url + '/' + str(arg)
            r = requests.get(req_url)
            return r.json()
        return wrapper
    return wrap


def dec_all_methods(decorator):
    """Decorates all the methods of a class"""
    def dectheclass(cls):
        for name, m in inspect.getmembers(cls, inspect.ismethod):
            setattr(cls, name, decorator(m))
        return cls
    return dectheclass
