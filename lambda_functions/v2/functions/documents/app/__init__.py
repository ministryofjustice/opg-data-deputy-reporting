from .api.resources import api as api_blueprint


def create_app(Flask):
    print("starting flask app")
    print(Flask)
    app = Flask(__name__)
    print(app)
    app.register_blueprint(api_blueprint)

    return app
