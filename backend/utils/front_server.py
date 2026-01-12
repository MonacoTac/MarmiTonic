
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import threading


class FrontendHTTPRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        directory = os.path.join(os.path.dirname(__file__), '..', '..', 'frontend')
        super().__init__(*args, directory=directory, **kwargs)

def start_frontend_server():
    server_address = ('', 8080)
    try:
        httpd = HTTPServer(server_address, FrontendHTTPRequestHandler)
        print(f"Starting frontend server on: http://localhost:8080")
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
    except Exception as e:
        print(f"Frontend server already running or failed: {e}")


