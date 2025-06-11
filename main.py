from werkzeug.serving import WSGIRequestHandler

from main.app import create_app

if __name__ == '__main__':
    app = create_app()
    WSGIRequestHandler.protocol_version = "HTTP/1.1"
    app.run()
