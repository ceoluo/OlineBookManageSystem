# from flask import Flask

from app import create_app

# app = Flask(__name__)
app = create_app()

# @app.route('/')
# def hello_world():
#     return 'Hello World!'


if __name__ == '__main__':
    app.run()