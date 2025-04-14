# serve_static.py
import http.server
import socketserver

PORT = 8888

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving static files at http://localhost:{PORT}/static/")
    httpd.serve_forever()