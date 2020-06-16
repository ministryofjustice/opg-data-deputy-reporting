from flask import Flask

from lambda_functions.v1.functions.flask_app import create_app


http_server = create_app(Flask)
