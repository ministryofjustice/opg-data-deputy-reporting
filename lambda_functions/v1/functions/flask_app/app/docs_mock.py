from flask import Flask

from . import create_app

http_server = create_app(Flask)
